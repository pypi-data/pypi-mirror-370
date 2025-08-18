let csrfToken = '_unset'

export async function post(endpoint?: string|undefined) {
    let url
    const options: RequestInit = {method: 'POST'}

    if (!endpoint || endpoint.startsWith('/')) {
        url = endpoint ? `${document.body.dataset.scriptPrefix}${endpoint.slice(1)}` : window.location.href

        if (csrfToken == '_unset') {
            csrfToken = (document.getElementById('csrfmiddlewaretoken') as HTMLInputElement).value
            if (! csrfToken) {
                throw new Error("Missing CSRF token")
            }
        }
        
        options.body = new FormData()
        options.body.append('csrfmiddlewaretoken', csrfToken)        
    }
    else {
        url = endpoint
    }

    return await fetch(url, options)
}

export async function postJson(endpoint?: string|undefined): Promise<{error?: string, [key: string]: any}> {
    let response
    try {
        response = await post(endpoint)
    }
    catch (err) {
        return {error: String(err)}
    }

    let data
    try {
        data = await response.json()
        if (data.error) {
            if (typeof(data.error) != 'string')
                data.error = String(data.error)
            return data
        }

        if (response.status < 200 || response.status >= 300)
            data = {error: `Error ${response.status}: ${response.statusText}`, ...data}
        return data
    }
    catch {
        if (response.status < 200 || response.status >= 300)
            return {error: `Error ${response.status}: ${response.statusText}`}
        else
            return {error: "Could not parse response as JSON"}
    }
}
