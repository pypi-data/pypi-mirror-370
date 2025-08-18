import type { Options } from 'select2'

/**
 * Initialize select2 from a <select> element.
 * 
 * Useful options:
 * - `url`: GET url 
 * - `allowClear`: set by default
 * - `tags`: if true, allow free text responses
 */
export function initSelect2(selector: string, options: Options & {url?: string} = {}) {
    if (options.theme === undefined) {
        options.theme = 'bootstrap-5'
        options.width = '100%'
    }

    if (options.allowClear == undefined) {
        options.allowClear = true
        options.placeholder = ''
    }

    if (options.url) {
        options.ajax = {
            url: options.url,
            data(params) {
                return {
                    q: (params as any).q,
                    page: params.page,
                }
            },
        }
    }

    return $(selector).select2(options) 
}
