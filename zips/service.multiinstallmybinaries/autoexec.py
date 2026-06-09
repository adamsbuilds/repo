from plugin import Installer
import json
import xbmc

m = Installer()

def main():
    try:
        xbmc.log('AUTOEXEC STARTED', xbmc.LOGINFO)
        m.create_folder(m.addon_data)
        xbmc.log(f'Addon data folder: {m.addon_data}', xbmc.LOGINFO)
        
        activate_setting = m.get_setting("activate_installer")
        xbmc.log(f'activate_installer setting: {activate_setting}', xbmc.LOGINFO)
        
        if activate_setting == 'true':
            xbmc.log('Installer activated, starting installation', xbmc.LOGINFO)
            m.installer()
        else:
            xbmc.log('Installer not activated, skipping', xbmc.LOGINFO)
            quit()
    except Exception as e:
        xbmc.log(f'ERROR in autoexec: {str(e)}', xbmc.LOGERROR)
        quit()

if __name__ == "__main__":
    main()
