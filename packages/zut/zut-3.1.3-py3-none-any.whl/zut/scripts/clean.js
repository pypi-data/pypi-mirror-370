//@ts-check
import path from 'path'
import fs from 'fs'

/**
 * Remove all entries with the given name, recursively from the given directory.
 * @param {string} dir 
 * @param {string} name 
 */
export function removeName(dir, name) {
    const handle = fs.opendirSync(dir)
    
    /** @type {fs.Dirent|null} */
    let entry

    while ((entry = handle.readSync()) !== null) {
        if (entry.name == '.venv') {
            continue
        }

        if (entry.name == name) {
            fs.rmSync(path.join(dir, entry.name), { recursive: true, force: true })
        }
        else if (entry.isDirectory()) {
            removeName(path.join(dir, entry.name), name)
        }
    }
    handle.closeSync()
}
