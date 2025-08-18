//@ts-check
import path from 'node:path'
import fs from 'node:fs'

/**
 * Return the list of Vite asset names (without extension) usable from templates,
 * associated to the absolute location of the source file. Example:(
 * 
 *      `core/layout => path/to/djangoapp/assets/core/layout.ts`
 *
 * @param {string|string[]} baseLocation
 * @param {string} baseName
 * @returns {{[name: string]: string}}
 */
export function getAssets(baseLocation, baseName = '') {
    /** @type {{[name: string]: string}} */
    const result = {}

    if (Array.isArray(baseLocation)) {
        for (const location of baseLocation) {
            for (const [entryName, entryLocation] of Object.entries(getAssets(location))) {
                result[entryName] = entryLocation
            }
        }

        return result
    }
    else {
        for (const dirent of fs.readdirSync(baseLocation, {withFileTypes: true})) {
            if (dirent.isDirectory()) {
                const subLocation = path.join(baseLocation, dirent.name)
                const subName = (baseName ? `${baseName}/` : '') + dirent.name
                for (const [entryName, entryLocation] of Object.entries(getAssets(subLocation, subName))) {
                    result[entryName] = entryLocation
                }
            }
            else if (dirent.name.endsWith('.ts')) {
                const entryLocation = path.join(baseLocation, dirent.name)
                const entryName = (baseName ? `${baseName}/` : '') + dirent.name.slice(0, -'.ts'.length)
                result[entryName] = entryLocation
            }
        }

        return result
    }
}
