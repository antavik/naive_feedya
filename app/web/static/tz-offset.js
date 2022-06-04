htmx.defineExtension('tz-offset', {
    onEvent: function (name, evt) {
        if (name === 'htmx:configRequest') {
            let date = new Date();
            evt.detail.headers['X-TZ-Offset'] = date.getTimezoneOffset();
        }
    }
});