function sendForm(data){
    const form = data.form;
    const url = data.url;
    const body = data.body;
    const action = data.action;

    $('#response_msg').hide();
    
    fetch(url, {
        method: 'POST',
        "body": body,
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(function (response) {
        return response.json();
    })
    .then(function (jsonResponse) {
        if(jsonResponse.success){
            $('#response_msg').removeClass('alert-warning').addClass('alert-success');
            $('#response_msg').show();
            if (action == 'create') {
                reset_form(form);
            }
        }else{
            $('#response_msg').removeClass('alert-success').addClass('alert-warning');
            $('#response_msg').show();
        }
        $('#response_msg').text(jsonResponse.msg);
    //   window.location.reload(true);
    })
    .catch(function (err) {
        $('#response_msg').text('An error occurred, please try again');
        $('#response_msg').removeClass('alert-success').addClass('alert-warning');
        $('#response_msg').show();
        console.log('An error occurred, please try again');
        console.log(err);
    })
}


function reset_form(elem){
    $(elem).find(':input')
        .not(':button, :submit, :reset, :hidden')
        .val('')
        .prop('checked', false)
        .prop('selected', false);
}

