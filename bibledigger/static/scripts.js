var lang_select = document.getElementById("language1");
var tran_select = document.getElementById("translation1");
var book_select = document.getElementById("book");
var chapter_select = document.getElementById("chapter");
var verse_select = document.getElementById("verse");
var lang_select2 = document.getElementById("language2");
var tran_select2 = document.getElementById("translation2");

function populateList(list1, list2, list2Name, anchor=1, input=0, list3=0, list4=0, list5=0) {

    var l2Name;
    if (list2Name.startsWith('translation')) {
        l2Name = list2Name.substr(0, list2Name.length - 1);
    } else {
        l2Name = list2Name;
    };

    fetch(`/${l2Name}/` + anchor).then(function(response) {

        response.json().then(function(data) {

            var optionHTML = '';

            for (var item of data.items) {
                optionHTML += '<option value="' + item.id + '">' + item.item + '</option>';
            }

            list2.innerHTML = optionHTML;

            $(`#${list2Name}`).selectpicker('refresh');

            var itemId;
            if (input === 0) {
                itemId = list2[0].value;
                if (anchor !== 1) {
                    anchor = itemId;
                };
            } else {
                if (list2Name.startsWith('translation')) {
                    itemId = input[0];
                } else if (list2Name === 'book') {
                    itemId = input[1];
                } else if (list2Name === 'chapter') {
                    itemId = input[2];
                } else if (list2Name === 'verse') {
                    itemId = input[3];
                };
                anchor = itemId;
            };

            $(`#${list2Name}`).selectpicker('val', itemId);
            if (list2Name === 'translation1') {
                populateList(tran_select, book_select, 'book', anchor, input,
                    book_select, chapter_select, verse_select);
            } else if (list2Name === 'book' && chapter_select !== null) {
                populateList(book_select, chapter_select, 'chapter', anchor, input,
                    chapter_select, verse_select);
            } else if (list2Name === 'chapter') {
                populateList(chapter_select, verse_select, 'verse', anchor, input);
            };
        });
    });
};
