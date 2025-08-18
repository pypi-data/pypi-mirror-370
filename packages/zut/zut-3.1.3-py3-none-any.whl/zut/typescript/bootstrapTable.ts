import type { BootstrapTableOptions } from 'bootstrap-table'

type ExtendedBootstrapTableOptions = BootstrapTableOptions & {
    showExport?: boolean
    exportTypes?: string[]
    exportOptions?: object
}

export function initBootstrapTable(selector: string, options: ExtendedBootstrapTableOptions = {}) {
    let form = undefined
    if (options.toolbar) {
        form = document.querySelector(`${options.toolbar} form`)
    }

    if (options.url === undefined) {
        options.url = './data'
        if (form) {
            options.url += `?${$(form).serialize()}`
        }
    }
    if (options.search === undefined) {
        options.search = true
    }
    if (options.pagination === undefined) {
        options.pagination = true
    }
    if (options.pageSize === undefined) {
        options.pageSize = 25
    }
    if (options.showExport === undefined) {
        options.showExport = true
    }
    if (options.exportTypes === undefined) {
        options.exportTypes = ["csv", "xlsx"]
    }
    if (options.exportOptions == undefined) {
        let exportName = selector.replace(/[^a-zA-Z0-9_]/g, '')
        if (exportName.endsWith('_table')) {
            exportName = exportName.substring(0, exportName.length - 6)
        }
        options.exportOptions = {
            fileName: function () { return exportName }
        }
    }
    
    return $(selector).bootstrapTable(options)
}
