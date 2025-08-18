//@ts-check
import path from 'path'
import fs from 'fs'
import zlib from 'zlib'
import { Readable } from 'stream'
import { finished } from 'stream/promises'
import { globSync } from 'glob'
import { ProxyAgent } from 'undici'

/**
 * Copy files after instrallation.
 * E.g. copy('select2/dist/js/i18n/*.js', 'static/lib', {base: 'node_modules'})
 * @param {string} pattern 
 * @param {string} target 
 * @param {Object} options
 * @param {string?} [options.base]
 */
export function copy(pattern, target, {base = null} = {}) {
    if (! base) {
        base = process.cwd()
    }

    const files = globSync(pattern, {cwd: base})
    if (files.length == 0) {
        console.error(`[copy] ${pattern}: no file`)
        return
    }
    
    console.log(`[copy] ${pattern}: ${files.length} file${files.length > 1 ? 's' : ''} ...`)
    
    for (const file of files) {
        const src = path.join(base, file)
        const dst = path.join(target, file)
        fs.mkdirSync(path.dirname(dst), {recursive: true})
        fs.copyFileSync(src, dst)
    }
}

/**
 * @param {string} url
 * @param {string} target
 * @param {Object} options
 * @param {boolean} [options.gunzip] Unzip the result data
 * @param {RegExp|string|null} [options.linkPattern] A regular expression matching the actual download URL (first capturing group).
 * @param {boolean} [options.ifChanged] Only download if the parsed URL changed (implies keepOrigin).
 * @param {boolean} [options.keepOrigin] Keep the metadata in a '.json' file.
 * @param {string} [options.proxyUrl] Proxy URL, e.g. http://proxy.lan:3128. Defaults to DOWNLOAD_PROXY_URL environment variable.
 */
export async function download(url, target, {gunzip = false, linkPattern = null, ifChanged = false, keepOrigin = false, proxyUrl = undefined} = {}) {
    if (proxyUrl === undefined) {
        proxyUrl = process.env.DOWNLOAD_PROXY_URL
    }

    /** @type {RequestInit} */
    const fetchOptions = {
        // @ts-ignore
        dispatcher: proxyUrl ? new ProxyAgent(proxyUrl) : undefined,
    }

    if (linkPattern) {
        const res = await fetch(url, fetchOptions)
        const indexContent = await res.text()
        const m = indexContent.match(linkPattern)
        if (! m) {
            console.error(`[download] could not find expected link pattern in ${url}`)
            return
        }

        url = m[1]
    }

    // Check if we need to redownload
    const metadataFile = `${target}.json`
    if (ifChanged) {
        keepOrigin = true

        if (fs.existsSync(target) && fs.existsSync(metadataFile)) {
            try {
                const metadata = JSON.parse(fs.readFileSync(metadataFile, {encoding:'utf-8'}))
                console.log(`[download] ${url}: skip`)
                if (metadata.url == url) {
                    return
                }
            }
            catch {
                // Malformed metadata, need to redownload
            }
        }
    }

    // Actual download
    console.log(`[download] ${url}`)
    fs.mkdirSync(path.dirname(target), {recursive: true})
    
    const res = await fetch(url, fetchOptions)
    if (res.body === null)
        throw new Error("Response body is null") 
    
    // @ts-ignore
    let stream = Readable.fromWeb(res.body)
    if (gunzip) {
        stream = stream.pipe(zlib.createGunzip())    
    }
    await finished(stream
        .pipe(fs.createWriteStream(target, { flags: 'w' }))
    )

    // Store metadata
    if (ifChanged) {
        fs.writeFileSync(metadataFile, JSON.stringify({
            url,
            timestamp: new Date().getTime(), // UTC
            name: path.basename(target),
            size: fs.statSync(target).size, // bytes
        }), {encoding:'utf-8'})
    }
}
