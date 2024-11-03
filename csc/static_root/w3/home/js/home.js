$(document).ready(() => {
    $('#near-me').click(function() {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const latitude = position.coords.latitude;
                    const longitude = position.coords.longitude;
                    if (latitude && longitude) {
                        window.location.href = `/centers_near_me/${latitude}/${longitude}`;
                    }
                }
            )
        }			
    });	
    
    // Pincode Search Toggle
    $('#pincode-checkbox-btn').click((e) => {
        if (e.target.checked == true) {
            $('#pincode-input-div').show();
            $('#pincode-input-div input').prop({'required': true, 'disabled': false});
            $('#state-input-div select').prop({'required': false, 'disabled': true});
            $('#state-input-div, #district-input-div, #block-input-div').hide();
        } else {
            $('#pincode-input-div').hide();
            $('#pincode-input-div input').prop({'required': false, 'disabled': true});
            $('#state-input-div select').prop({'required': true, 'disabled': false});
            $('#state-input-div, #district-input-div, #block-input-div').show();
        }
    })
});