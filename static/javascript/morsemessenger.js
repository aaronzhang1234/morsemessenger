$(document).ready(function(){
    var pusher = new Pusher(pusherKey);
    var channel = pusher.subscribe(pusherChannel);
    channel.bind(pusherEvent, function(data){
       $('#messagearea ul:first-child').append('<li class="morsemessage">'+data.message+'</li>');
    })
    $('#messagearea').css("overflow-y", "scroll");
});  
