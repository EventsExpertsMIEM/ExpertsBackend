$(function() {
    $("#f_create_event").submit(function(e) {
        e.preventDefault();
        $.ajax({
            url: "/api/event_create",
            type: "POST",
            data: JSON.stringify({"name": $(".create_event_name").val(),
                                  "sm_description": $(".create_event_sm_description").val(),
                                  "description": $(".create_event_description").val(),
                                  "date_time": $(".create_event_date_time").val(),
                                  "phone": $(".create_event_phone").val(),
                                  "mail": $(".create_event_mail").val(),
                                  "presenters": $(".create_event_presenters").val()
                                }),
            contentType: "application/json",
            dataType: "json",
            success: function(data){
                $('#message').html(data["description"]);
                setTimeout(
                    function() {
                    window.location = '/event/' + data["params"];
                    }, 2000
                )
            },
            error: function(data){
                $('#message').html(data.responseJSON['error']);
            }
        });
        $("#f_create_event").trigger('reset');
    });
});