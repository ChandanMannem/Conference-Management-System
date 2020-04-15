        jQuery(function ($) {
            $('.table').footable({
                "paging": {
                    "enabled": true
                },
                "filtering": {
                    "enabled": true
                },
                "sorting": {
                    "enabled": true
                }
            });
            $(document).ready(function () {
                $('.select-state').selectize({
                    maxItems: 2,
                    onChange: function(value) {
                            var a = document.activeElement.id;
                            var paper_id = a.split("-");
                            $("#paper_id").val(paper_id[0]);
                           $("#action").val(value);
                     },
                     onBlur: function(){
                          $("#submit_button").click();
                     }
                });

                $('.select-status').selectize({
                    create: true,
                    sortField: 'text',
                    onChange: function(value){
                          $("#action").val(value);
                          $("#action_button").click();
                     },
                     onFocus: function(){
                          var a = document.activeElement.id;
                          var paper_id = a.split("-");
                          $("#paper_id").val(paper_id[0]);
                     }
                });
            });

        });