(function(pythia) {
  $.ajaxSetup({
    beforeSend: function() {
      if (typeof(tinyMCE) != "undefined") {
        pythia.activeEdColour = $(tinyMCE.activeEditor.getContainer()).css(
          'border-color');
        $(tinyMCE.activeEditor.getContainer()).css(
          'border-color', '#bb0000');
      }
    },
    complete: function() {
      if (typeof(tinyMCE) != "undefined") {
        $(tinyMCE.activeEditor.getContainer()).css(
          'border-color', pythia.activeEdColour);
        hasChanged = false; // hasChanged defined in "admin/change_form.html"
      }
    }
  });

  pythia.inlineEditUrls = new Object();

  pythia.inlineSave = (function(url, data) {
    $.ajax({
      type: 'POST', url: url, data: data
    });
  });

  pythia.getCsrfToken = (function($el) {
    return $el.closest('form').find('input[name=csrfmiddlewaretoken]').val();
  });

  // inline tinyMCE editing
  pythia.tinyMCEinit = (function(ed) {
    ed.on('init', function(args) {
      // create the text block
      ed.pythiaText = $('<div class="tinymce-wrap">' + ed.getContent() +
                        '</div>');

      ed.pythiaText.click(function() {
        pythia.inlineShowTinyMCE(ed);
      });

      ed.csrftoken = pythia.getCsrfToken($(ed.getElement()));

      // insert the text block
      $(ed.getContainer()).before(ed.pythiaText);

      pythia.inlineHideTinyMCE(ed);

      var save = function() {
        ed.pythiaText.html(ed.getContent());
        data = $(ed.getElement()).parents("form").serialize()
        if (pythia.inlineEditUrls[ed.id]) 
           pythia.inlineSave(pythia.inlineEditUrls[ed.id], data);
      };

      // attach events for AJAX save
      ed.on('change', function(args) {
        save();
      });

      ed.on('blur', function() {
        save();
        pythia.inlineHideTinyMCE(ed);
      });
    });
  });

  pythia.inlineHideTinyMCE = (function(ed) {
    ed.hide();
    $(ed.getElement()).hide();
    if (!ed.getContent()) {
      ed.pythiaText.html('<span>&lt;Click here to edit&gt;</span>');
    }
    ed.pythiaText.show();
  });

  pythia.inlineShowTinyMCE = (function(ed) {
    ed.show();
    ed.focus();
    ed.pythiaText.hide();
  });

  pythia.inlineEditTextarea = (function(id, url) {
    pythia.inlineEditUrls[id] = null;
    if (url != "None")
        pythia.inlineEditUrls[id] = url;
    $(function() {
      tinyMCE.init({
        menubar: false,
        toolbar: 'undo redo | bold italic underline subscript superscript | removeformat | bullist numlist | link charmap | table | spellchecker | code',
        selector: '#' + id,
        plugins: [
          'advlist autolink lists link charmap print preview anchor',
          'searchreplace visualblocks code fullscreen autoresize',
          'insertdatetime contextmenu paste wordcount spellchecker table'
        ],
        spellchecker_languages : "+English=en-au",
        spellchecker_rpc_url: '/spillchuck/',
        setup: pythia.tinyMCEinit
      });
    });
  });

  // handsontable
  pythia.handsontable = (function(input_id, url) {
    $(function() {
      var input = $('#' + input_id);
      var table = $('#dataTable' + input_id);

      table.handsontable({
        data: $.parseJSON(input.val() || '[[""]]'),
        afterChange: function(change, source) {
          if (source != 'loadData') {
            input.val(JSON.stringify(this.getData()));
            var data = input.parents("form").serialize();
            pythia.inlineSave(url, data);
          }
        }
      });

      input.hide();
    });
  });

  // textinput
  pythia.inlineEditTextInput = (function(input_id, url) {
    $(function() {
      pythia.inlineEditWidget(input_id, url);
    });
  });

  // select
  pythia.inlineEditSelect = (function(input_id, url) {
    $(function() {
      pythia.inlineEditWidget(input_id, url, function(select) {
        return select.children('option:selected').text();
      });
    });
  });

  // widget
  pythia.inlineEditWidget = (function(input_id, url, text_getter) {
    $(function() {
      text_getter = text_getter || function(input) { return input.val(); };
      var input = $('#' + input_id);
      var input_name = input.attr('name');
      var input_val = input.val();
      var text = $('<div class="tinymce-wrap shrinkwrap">' +
                   (text_getter(input) || '&lt;Click here to edit&gt;') +
                   '</div>');
      var csrftoken = pythia.getCsrfToken(input);

      text.click(function() {
        input.show();
        input.focus();
        text.hide();
      });

      input.focusout(function() {
        if (input_val != input.val()) {
          var data = input.parents("form").serialize();
          pythia.inlineSave(url, data);
          text.first().html(text_getter(input) ||
                            '&lt;Click here to edit&gt;');
        }
        input.hide();
        text.show();
      });

      // insert the text block
      input.before(text);

      // decide what to show and hide
      if (input_val) {
        input.focusout();
      } else {
        text.hide();
        input.show();
        // we cannot do focus here because another widget could "steal" it
        // (causing the focusout being triggered on this field)
      }
    });
  });

  pythia.deployPopup = (function(triggeringLink) {
    var name = triggeringLink.id.replace(/^add_/, '');
    name = id_to_windowname(name);
    href = triggeringLink.href
    if (href.indexOf('?') == -1) {
        href += '?_popup=1';
    } else {
        href  += '&_popup=1';
    }
    var win = window.open(href, name, 'height=600,width=1200,resizable=yes,scrollbars=yes');
    win.focus();
    return false;
  });

  pythia.returnFromPopup = (function() {
    try {
        window.opener.pythia.refresh();
    } catch (err) {}
    window.close();
    return false;
  });

  pythia.refresh = (function() {
    if ($("id_submit_button").length) {
        $("id_submit_button").select();
    } else {
        location.reload();
    }
    return false;
  });

  pythia.areasWidgetWrapper = function(id) {
    $(function() {
      var parent_select = $('#' + id);
      var div = parent_select.parent('div');

      parent_select.hide();
      div.next('p').hide();  // the annoying help text

      var groups = {};
      var type = null;
      // groupBy area type :)
      parent_select.find('option').each(function(i, option) {
        type = option.text.substr(1, option.text.indexOf(']') - 1);
        if (!(type in groups))
          groups[type] = Array();
        groups[type].push(option);
      });

      // iterate through area types
      for (var type in groups) {
        // prepare the new select
        var select_id = 'id_pythia_areasWidgetWrapper_' + type;
        var select = $('<select id="' + select_id +
                       //'" multiple="multiple" style="width: auto; float:right !important;" size="'+  
                       '" multiple class="form-control" style="width: auto; float:right !important;" size="'+  
                       groups[type].length + '"/>');
        // add onChange handler
        select.change(function() {
          $(this).find('option').each(function(i, option) {
            var parent_option = parent_select.find('option[value=' +
                                                   option.value + ']');
            if ($(option).is(':selected'))
              parent_option.attr('selected', 'selected');
            else
              parent_option.removeAttr('selected');
          });
        });

        // prepare individual options for this select
        for (var index in groups[type]) {
          var parent_option = groups[type][index];
          var option = $('<option value="' + parent_option.value + '">' +
                         parent_option.text.substr(
                             parent_option.text.indexOf(']') + 2) +
                         '</option>');
          if ($(parent_option).is(':selected'))
            option.attr('selected', 'selected');
          select.append(option);
        }

        // add the new select
        var p = $('<div class="row"><div class="col-md-12"><div class="areasWidgetWrapper areasWidgetWrapper-' +
                  type.replace(' ', '_') + '"></div></div></div>');
        //var p = $('<div class="col-xs-4"><div class="areasWidgetWrapper areasWidgetWrapper-' +
        //          type.replace(' ', '_') + '"></div></div>');
        p.append('<label for="' + select_id + '">' + type + '</label');
        p.append(select);
        div.append(p);
      }
    });
  };

})(window.pythia = window.pythia || {});


