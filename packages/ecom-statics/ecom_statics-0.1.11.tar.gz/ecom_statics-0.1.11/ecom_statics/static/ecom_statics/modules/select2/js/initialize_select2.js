$(document).ready(() => {
    $('select').each((_, select_element) => {
        const select = $(select_element);
        const is_multiple = select.is('[multiple]');
        
        let config = {
            width: '100%'
        };

        if (is_multiple) config.placeholder = select.attr('placeholder');

        if (!is_multiple && select.children().not('[value=""]').length <= 3) config.minimumResultsForSearch = Infinity;

        select.select2(config);
    });
});
