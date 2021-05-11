htmx.defineExtension('oauth-header', {
    onEvent : function(name, evt) {
        if (name === "htmx:configRequest") {
            let token = window.sessionStorage.getItem('access_token');
            let tokenType = window.sessionStorage.getItem('token_type');
            evt.detail.headers['Authorization'] = `${tokenType} ${token}`;
        }
        return true;
    }
})