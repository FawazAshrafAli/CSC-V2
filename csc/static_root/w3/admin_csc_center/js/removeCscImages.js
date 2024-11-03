function removeCscLogo(cscId) {
    $.ajax({
        type: 'POST',
        url: `/admin/remove_csc_logo/${cscId}`,
        dataType: 'json',
        success: (data) => {
            if (data.message) {
                console.log(data.message);
                $('#current-csc-logo').hide();
            };
        },
        error: (error) => {
            console.error("Error: ", error);
        },
    });
};

function removeCscBanner(cscId) {
    $.ajax({
        type: 'POST',
        url: `/admin/remove_csc_banner/${cscId}`,
        dataType: 'json',
        success: (data) => {
            if (data.message) {
                console.log(data.message);
                $('#current-csc-banner').hide();
            };
        },
        error: (error) => {
            console.error("Error: ", error);
        },
    });
};