const initMercadoPagoButton = function (pubKey, prevenceId) {
    const mp = new MercadoPago(pubKey, {
        locale: 'pt-BR'
    });

    mp.checkout({
        preference: {
            id: prevenceId
        },
        render: {
            container: '.cho-container',
            type: 'wallet',
        }
    });
}

// TODO: why $('#mp_button button').click doesn't work?
$("#mp_button").click(function (e) {
    e.preventDefault();
})