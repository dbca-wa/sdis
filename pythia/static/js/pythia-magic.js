$(function() {
    $("li.dropdown li.active").parents("li.dropdown").addClass("active");
    function textAreaAdjust(o) {
        o.target.style.height = "1.5em";
        if (o.target.scrollHeight > $(o.target).height()) {
          o.target.style.height = "1px";
          o.target.style.height = (25 + o.target.scrollHeight) + "px";
        }
    }
    //$("textarea").keyup(textAreaAdjust).keyup();
    //tinyMCE.init({selector: "textarea.vLargeTextField"});
    $("body").on('keyup', 'textarea', textAreaAdjust);
    $("body textarea").keyup();
});
