htmx.defineExtension('oauth-token-save', {
    transformResponse : function(text, xhr, elt) {
        let tokenMeta = JSON.parse(text);
        if ('access_token' in tokenMeta && 'token_type' in tokenMeta) {
            window.sessionStorage.setItem('access_token', tokenMeta['access_token']);
            window.sessionStorage.setItem('token_type', tokenMeta['token_type']);
            location.reload();
        }
        return '<center><p>Reloading...</p></center>';
    }
})