$(document).ready(function(){  
    $(document).on("click", ".b_join", function(){
        var page = $(this);
        $.ajax({
            url: "/api/join",
            type: "POST",
            data: JSON.stringify({"event_id": page.attr('id')}),
            contentType: "application/json",
            dataType: "json",
            success: function(data){
                if(data['status'] == 'ok') {
                    $("#text_join").text("Спасибо за подачу заявки!");
                    page.remove();
                }
            },
            error: function(data){
                $("#text_join").text(data.responseJSON['error']);
            }
        });
    });
});