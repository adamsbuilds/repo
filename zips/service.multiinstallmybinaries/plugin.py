import xbmc
import xbmcvfs
import xbmcaddon
import os
import json
import time
    
class Installer:
    
    addon_data = xbmcvfs.translatePath(xbmcaddon.Addon().getAddonInfo('profile'))
    get_setting = xbmcaddon.Addon().getSetting
    set_setting = xbmcaddon.Addon().setSetting
    addon_json = xbmcvfs.translatePath('special://home/addons/service.multiinstallmybinaries/resources/addons.json')
    
    def create_folder(self, folder_path):
        if not xbmcvfs.exists(folder_path):
            return xbmcvfs.mkdir(folder_path)
        
    def installer(self):
        xbmc.log('INSTALLER STARTED', xbmc.LOGINFO)
        xbmc.sleep(5000)
        
        try:
            xbmc.log(f'Reading addon_json from: {self.addon_json}', xbmc.LOGINFO)
            with open(self.addon_json, 'r', encoding='utf-8', errors='ignore') as f:
                addon_list = json.loads(f.read())
            xbmc.log(f'Addon list loaded successfully: {addon_list}', xbmc.LOGINFO)
        except Exception as e:
            xbmc.log(f'ERROR reading addon_json: {str(e)}', xbmc.LOGERROR)
            self.set_setting('activate_installer', 'true')
            return
        
        failed = []
        for addon in addon_list.keys():
            try:
                name = addon_list[addon]
                plugin_id = addon_list[addon]['plugin_id']
                xbmc.log(f'Installing addon: {plugin_id}', xbmc.LOGINFO)
                install = self.install_addon(plugin_id)
                if install is not True:  # ← FIXED: Moved inside the loop with correct indentation
                    xbmc.log(f'Failed to install: {plugin_id}', xbmc.LOGERROR)
                    failed.append([name, plugin_id])
                else:
                    xbmc.log(f'Successfully installed: {plugin_id}', xbmc.LOGINFO)
            except Exception as e:
                xbmc.log(f'ERROR processing addon {addon}: {str(e)}', xbmc.LOGERROR)
                failed.append([addon, str(e)])
        
        if len(failed) == 0:
            xbmc.log('All addons installed successfully', xbmc.LOGINFO)
            self.set_setting('activate_installer', 'false')
        else:
            xbmc.log(f'Failed addons: {failed}', xbmc.LOGERROR)
            self.set_setting('activate_installer', 'true')
    
    def install_addon(self, plugin_id):
        try:
            if xbmc.getCondVisibility(f'System.HasAddon({plugin_id})'):
                xbmc.log(f'Addon already installed: {plugin_id}', xbmc.LOGINFO)
                return True
            
            xbmc.log(f'Executing InstallAddon for: {plugin_id}', xbmc.LOGINFO)
            xbmc.executebuiltin(f'InstallAddon({plugin_id})')
            clicked = False
            start = time.time()
            timeout = 60  # ← INCREASED FROM 20 TO 60 SECONDS FOR BINARY ADDONS
            
            while not self.isinstalled(plugin_id):
                elapsed = time.time() - start
                if elapsed >= timeout:
                    xbmc.log(f'Installation timeout for {plugin_id} after {timeout} seconds', xbmc.LOGERROR)
                    return False
                
                xbmc.sleep(500)
                
                if xbmc.getCondVisibility('Window.IsTopMost(yesnodialog)') and not clicked:
                    xbmc.log(f'Dialog detected, auto-clicking for {plugin_id}', xbmc.LOGINFO)
                    xbmc.executebuiltin('SendClick(yesnodialog, 11)')
                    clicked = True
            
            xbmc.log(f'Installation completed: {plugin_id}', xbmc.LOGINFO)
            return True
        except Exception as e:
            xbmc.log(f'ERROR installing {plugin_id}: {str(e)}', xbmc.LOGERROR)
            return False

    def isinstalled(self, addonid):
        try:
            query = '{ "jsonrpc": "2.0", "id": 1, "method": "Addons.GetAddonDetails", "params": { "addonid": "%s", "properties" : ["name", "thumbnail", "fanart", "enabled", "installed", "path", "dependencies"] } }' % addonid
            addonDetails = xbmc.executeJSONRPC(query)
            details_result = json.loads(addonDetails)
            
            if "error" in details_result:
                xbmc.log(f'Error querying addon {addonid}: {details_result["error"]}', xbmc.LOGDEBUG)
                return False
            elif details_result['result']['addon']['installed'] == True:
                xbmc.log(f'Addon confirmed installed: {addonid}', xbmc.LOGDEBUG)
                return True
            else:
                xbmc.log(f'Addon not yet installed: {addonid}', xbmc.LOGDEBUG)
                return False
        except Exception as e:
            xbmc.log(f'ERROR checking if {addonid} is installed: {str(e)}', xbmc.LOGERROR)
            return False
