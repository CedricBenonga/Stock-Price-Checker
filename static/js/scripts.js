$(function() {
    $("#datepicker").datepicker({
        dateFormat: "yy-mm-dd",
        onSelect: function(){
            var selected = $(this).datepicker("getDate");
            alert(selected);
        }
    });
});