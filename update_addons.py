#!/usr/bin/env python3
"""
Script to automatically update addons.xml with new addon versions
and generate MD5 hash.

This script:
1. Scans zips folder for new/updated addon zip files
2. Extracts version from zip filename (addon-id-version.zip)
3. Extracts addon.xml from the zip and updates main addons.xml
4. Generates MD5 hash for the updated addons.xml
"""

import os
import re
import hashlib
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

class AddonsUpdater:
    def __init__(self):
        self.zips_path = 'zips'
        self.addons_xml_path = os.path.join(self.zips_path, 'addons.xml')
        self.addons_md5_path = os.path.join(self.zips_path, 'addons.md5')
        self.updated = False
        
    def extract_version_from_filename(self, filename):
        """
        Extract addon ID and version from zip filename.
        Expected format: addon-id-version.zip
        Example: plugin.program.adamswizard-1.0.zip
        """
        if not filename.endswith('.zip'):
            return None, None
            
        # Remove .zip extension
        name_without_ext = filename[:-4]
        
        # Find the last hyphen to split addon-id and version
        # This handles addon IDs with hyphens like plugin.program.xyz-1.0
        match = re.match(r'^(.+)-(\d+\.\d+(?:\.\d+)?)$', name_without_ext)
        
        if match:
            addon_id = match.group(1)
            version = match.group(2)
            return addon_id, version
        
        return None, None
    
    def extract_addon_xml_from_zip(self, zip_path, addon_id):
        """
        Extract addon.xml from zip file.
        The addon.xml should be at: addon-id/addon.xml inside the zip
        """
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Look for addon.xml in the expected path
                addon_xml_path = f'{addon_id}/addon.xml'
                
                if addon_xml_path in zip_ref.namelist():
                    return zip_ref.read(addon_xml_path).decode('utf-8')
        except Exception as e:
            print(f"Error extracting addon.xml from {zip_path}: {e}")
        
        return None
    
    def parse_addon_xml(self, xml_content):
        """Parse addon.xml and extract addon metadata"""
        try:
            root = ET.fromstring(xml_content)
            return root
        except Exception as e:
            print(f"Error parsing addon.xml: {e}")
            return None
    
    def update_addons_xml(self):
        """
        Scan zips folder and update addons.xml with new versions
        """
        if not os.path.exists(self.addons_xml_path):
            print(f"Error: {self.addons_xml_path} not found")
            return False
        
        # Parse existing addons.xml
        try:
            tree = ET.parse(self.addons_xml_path)
            root = tree.getroot()
        except Exception as e:
            print(f"Error parsing existing addons.xml: {e}")
            return False
        
        # Get all zip files in zips folder
        zip_files = {}
        for addon_folder in os.listdir(self.zips_path):
            folder_path = os.path.join(self.zips_path, addon_folder)
            
            # Skip if not a directory
            if not os.path.isdir(folder_path):
                continue
            
            # Look for zip files in this folder
            for filename in os.listdir(folder_path):
                if filename.endswith('.zip'):
                    addon_id, version = self.extract_version_from_filename(filename)
                    
                    if addon_id and version:
                        zip_path = os.path.join(folder_path, filename)
                        
                        # Keep track of the latest version
                        if addon_id not in zip_files or self.compare_versions(version, zip_files[addon_id]['version']) > 0:
                            zip_files[addon_id] = {
                                'version': version,
                                'zip_path': zip_path,
                                'filename': filename
                            }
        
        # Update addons.xml with new versions
        for addon_id, zip_info in zip_files.items():
            version = zip_info['version']
            zip_path = zip_info['zip_path']
            
            print(f"Processing {addon_id} v{version}...")
            
            # Extract addon.xml from zip
            addon_xml_content = self.extract_addon_xml_from_zip(zip_path, addon_id)
            
            if not addon_xml_content:
                print(f"  Warning: Could not extract addon.xml from {zip_info['filename']}")
                continue
            
            # Parse the addon.xml
            addon_element = self.parse_addon_xml(addon_xml_content)
            if not addon_element:
                continue
            
            # Update version in the addon element
            addon_element.set('version', version)
            
            # Find existing addon in addons.xml
            existing_addon = root.find(f".//addon[@id='{addon_id}']")
            
            if existing_addon is not None:
                # Update existing addon
                addon_index = list(root).index(existing_addon)
                root.remove(existing_addon)
                root.insert(addon_index, addon_element)
                print(f"  ✓ Updated {addon_id} to version {version}")
                self.updated = True
            else:
                # Add new addon
                root.append(addon_element)
                print(f"  ✓ Added new addon {addon_id} version {version}")
                self.updated = True
        
        # Save updated addons.xml if changes were made
        if self.updated:
            try:
                tree.write(self.addons_xml_path, encoding='utf-8', xml_declaration=True)
                print(f"\n✓ Updated {self.addons_xml_path}")
                return True
            except Exception as e:
                print(f"Error saving addons.xml: {e}")
                return False
        else:
            print("No updates needed for addons.xml")
            return True
    
    def compare_versions(self, v1, v2):
        """
        Compare two version strings.
        Returns: 1 if v1 > v2, -1 if v1 < v2, 0 if equal
        """
        def parse_version(v):
            return [int(x) for x in v.split('.')]
        
        try:
            parts1 = parse_version(v1)
            parts2 = parse_version(v2)
            
            for p1, p2 in zip(parts1, parts2):
                if p1 > p2:
                    return 1
                elif p1 < p2:
                    return -1
            
            if len(parts1) > len(parts2):
                return 1
            elif len(parts1) < len(parts2):
                return -1
            
            return 0
        except:
            return 0
    
    def generate_md5(self):
        """Generate MD5 hash for addons.xml"""
        try:
            with open(self.addons_xml_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            md5_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
            
            with open(self.addons_md5_path, 'w') as f:
                f.write(md5_hash)
            
            print(f"\n✓ Generated MD5: {md5_hash}")
            return True
        except Exception as e:
            print(f"Error generating MD5: {e}")
            return False
    
    def run(self):
        """Run the full update process"""
        print("Starting addons.xml update process...\n")
        
        if self.update_addons_xml():
            self.generate_md5()
            print("\n✓ Process completed successfully!")
            return True
        else:
            print("\n✗ Process failed!")
            return False

if __name__ == "__main__":
    updater = AddonsUpdater()
    updater.run()
