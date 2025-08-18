const _messagesFixedAfter = parseInt(document.body.dataset.messagesFixedAfter ?? '75')
const _messagesDiv = document.getElementById('messages')!
const _messagesContentDiv = document.getElementById('messages-content')!
const _messagesClosedAll = document.getElementById('messages-close-all')

/**
 * Add a message with the given level.
 */
export function addMessage(level: 'ERROR'|'WARNING'|'INFO'|'SUCCESS'|'DEBUG', html: string) {
    let color = 'primary'
    if (level) {
        switch (level.toUpperCase()) {
            case 'DEBUG': color = 'secondary'; break
            case 'INFO': color = 'info'; break
            case 'SUCCESS': color = 'success'; break
            case 'WARNING': color = 'warning'; break
            case 'ERROR': color = 'danger'; break
        }
    }

    // Create message element
    /** @type {HTMLDivElement} */
    const messageDiv = document.createElement('div')
    messageDiv.className = `alert alert-${color} alert-dismissible fade show`
    messageDiv.role = 'alert'
    messageDiv.innerHTML = `${html}<button type="button" class="btn-close" data-bs-dismiss="alert"></button>`
    _messagesContentDiv.appendChild(messageDiv)

    // Fix the messages container at the top of the screen if scrolling above 75 px
    if (_messagesFixedAfter > 0 && window.scrollY > _messagesFixedAfter) {
        _messagesDiv.classList.add('fixed-messages') // see layout.css
    }

    return messageDiv
}

export function clearMessages() {
    while (_messagesContentDiv.firstChild) {
        _messagesContentDiv.removeChild(this._content.lastChild)
    }

    if (_messagesClosedAll) {
        _messagesClosedAll.classList.add('d-none')
    }
}

function messagesUpdate() {
    if (_messagesContentDiv.childElementCount >= 2) {
        if (_messagesClosedAll) {
            _messagesClosedAll.classList.remove('d-none')
        }
    }
    else {
        if (_messagesClosedAll) {
            _messagesClosedAll.classList.add('d-none')
        }
        
        if (_messagesFixedAfter > 0) {
            if (_messagesContentDiv.childElementCount == 0) {
                _messagesDiv.classList.remove('fixed-messages')
            }
        }
    }
}

if (_messagesClosedAll) {
    _messagesClosedAll.querySelector('a')!.addEventListener('click', ev => {
        ev.preventDefault()
        clearMessages()
    })
}

new MutationObserver(messagesUpdate).observe(_messagesContentDiv, {childList: true})
messagesUpdate()
