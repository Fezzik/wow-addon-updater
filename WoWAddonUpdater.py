import zipfile, configparser
from os.path import isfile
import SiteHandler
import packages.requests as requests


def confirmExit():
    input('\nPress the Enter key to exit')
    exit(0)


class AddonUpdater:
    def __init__(self):
        print('')

        # Read config file
        if not isfile('config.ini'):
            print('Failed to read configuration file. Are you sure there is a file called "config.ini"?\n')
            confirmExit()

        config = configparser.ConfigParser()
        config.read('config.ini')

        try:
            self.WOW_ADDON_LOCATION = config['WOW ADDON UPDATER']['WoW Addon Location']
            self.ADDON_LIST_FILE = config['WOW ADDON UPDATER']['Addon List File']
            self.INSTALLED_VERS_FILE = config['WOW ADDON UPDATER']['Installed Versions File']
            self.AUTO_CLOSE = config['WOW ADDON UPDATER']['Close Automatically When Completed']
        except Exception:
            print('Failed to parse configuration file. Are you sure it is formatted correctly?\n')
            confirmExit()

        if not isfile(self.ADDON_LIST_FILE):
            print('Failed to read addon list file. Are you sure the file exists?\n')
            confirmExit()

        if not isfile(self.INSTALLED_VERS_FILE):
            with open(self.INSTALLED_VERS_FILE, 'w') as newInstalledVersFile:
                newInstalledVers = configparser.ConfigParser()
                newInstalledVers['Installed Versions'] = {}
                newInstalledVers.write(newInstalledVersFile)
        return

    def update(self):
        # Main process (yes I formatted the project badly)
        uberlist = []
        with open(self.ADDON_LIST_FILE, "r") as fin:
            for line in fin:
                current_node = []
                line = line.rstrip('\n')
                if not line or line.startswith('#'):
                    continue
                currentVersion = SiteHandler.getCurrentVersion(line)
                if currentVersion is None:
                    currentVersion = 'Not Available'
                current_node.append(line.split("/")[-1])
                current_node.append(SiteHandler.getCurrentVersion(line))
                installedVersion = self.getInstalledVersion(line)
                if not currentVersion == installedVersion:
                    print('Installing/updating addon: ' + line + ' to version: ' + currentVersion + '\n')
                    ziploc = SiteHandler.findZiploc(line)
                    SiteHandler.installAddon(ziploc, self.WOW_ADDON_LOCATION)
                    current_node.append(self.getInstalledVersion(line))
                    if currentVersion is not '':
                        self.setInstalledVersion(line, currentVersion)
                else:
                    print(line + ' version ' + currentVersion + ' is up to date.\n')
                    current_node.append("Up to date")
                uberlist.append(current_node)
        if self.AUTO_CLOSE == 'False':
            col_width = max(len(word) for row in uberlist for word in row) + 2  # padding
            print("".join(word.ljust(col_width) for word in ("Name","Iversion","Cversion")))
            for row in uberlist:
                print("".join(word.ljust(col_width) for word in row), end='\n')
            confirmExit()

    def getInstalledVersion(self, addonpage):
        addonName = addonpage.replace('https://mods.curse.com/addons/wow/', '')
        addonName = addonName.replace('https://www.curseforge.com/wow/addons/', '')
        addonName = addonName.replace('https://wow.curseforge.com/projects/', '')
        addonName = addonName.replace('http://www.wowinterface.com/downloads/', '')
        if(addonName.startswith('https://git.tukui.org/')):
            addonName = addonName.split("/")[-1]
        installedVers = configparser.ConfigParser()
        installedVers.read(self.INSTALLED_VERS_FILE)
        try:
            return installedVers['Installed Versions'][addonName]
        except Exception:
            return 'version not found'

    def setInstalledVersion(self, addonpage, currentVersion):
        addonName = addonpage.replace('https://mods.curse.com/addons/wow/', '')
        addonName = addonName.replace('https://www.curseforge.com/wow/addons/', '')
        addonName = addonName.replace('https://wow.curseforge.com/projects/', '')
        addonName = addonName.replace('http://www.wowinterface.com/downloads/', '')
        if(addonName.startswith('https://git.tukui.org/')):
            addonName = addonName.split("/")[-1]
        installedVers = configparser.ConfigParser()
        installedVers.read(self.INSTALLED_VERS_FILE)
        installedVers.set('Installed Versions', addonName, currentVersion)
        with open(self.INSTALLED_VERS_FILE, 'w') as installedVersFile:
            installedVers.write(installedVersFile)


def main():
    addonupdater = AddonUpdater()
    addonupdater.update()
    return


if __name__ == "__main__":
    # execute only if run as a script
    main()
