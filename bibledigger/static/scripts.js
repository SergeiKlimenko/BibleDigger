var lang_select = document.getElementById("language1");
var tran_select = document.getElementById("translation1");
var book_select = document.getElementById("book");
var chapter_select = document.getElementById("chapter");
var verse_select = document.getElementById("verse");
var lang_select2 = document.getElementById("language2");
var tran_select2 = document.getElementById("translation2");


if (document.getElementsByClassName('nav-item nav-link active')[0] !== undefined) {
    document.getElementsByClassName('nav-item nav-link active')[0].classList.remove('active');
};


function populateList(list1, list2, list2Name, anchor = 1, input = 0, list3 = 0, list4 = 0, list5 = 0, book = null, chapter = null) {

    var l2Name;
    if (list2Name.startsWith('translation')) {
        l2Name = list2Name.substr(0, list2Name.length - 1);
    } else {
        l2Name = list2Name;
    };

    var route = `/${l2Name}/` + anchor;
    if (list2Name === 'chapter') {
        route += `/${book_select.value}`;
    } else if (list2Name === 'verse') {
        route += `/${book_select.value}/${chapter_select.value}`;
    };

    fetch(route).then(function(response) {

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
                if (list2Name === 'book') {
                    book = itemId;
                } else if (list2Name === 'chapter') {
                    chapter = itemId;
                } else {
                    anchor = itemId;
                };

            } else {
                if (list2Name.startsWith('translation')) {
                    itemId = input[0];
                    anchor = itemId;
                } else if (list2Name === 'book') {
                    itemId = input[1];
                    book = itemId;
                } else if (list2Name === 'chapter') {
                    itemId = input[2];
                    chapter = itemId;
                } else if (list2Name === 'verse') {
                    itemId = input[3];
                };
            };

            $(`#${list2Name}`).selectpicker('val', itemId);
            if (list2Name === 'translation1' && book_select !== null) {
                populateList(tran_select, book_select, 'book', anchor, input,
                    book_select, chapter_select, verse_select);
            } else if (list2Name === 'book' && chapter_select !== null) {
                populateList(book_select, chapter_select, 'chapter', anchor, input,
                    chapter_select, verse_select, list5 = 0, book);
            } else if (list2Name === 'chapter') {
                populateList(chapter_select, verse_select, 'verse', anchor, input, list3 = 0, list4 = 0, list5 = 0, book, chapter);
            };
        });
    });
};


function render(aggreg, page, baseLink) {
    var pageNumber1, pageNumber2;
    pageNumber1 = document.getElementById('pageNumber1');
    pageNumber2 = document.getElementById('pageNumber2');
    var first1, previous1, next1, last1;
    first1 = document.getElementById('first1');
    previous1 = document.getElementById('previous1');
    next1 = document.getElementById('next1');
    last1 = document.getElementById('last1');
    var first2, previous2, next2, last2;
    first2 = document.getElementById('first2');
    previous2 = document.getElementById('previous2');
    next2 = document.getElementById('next2');
    last2 = document.getElementById('last2');

    var html = ``;

    // Concordance
    if (aggreg[1][0].length === 6 || aggreg[1][0].length === 5) {
        for (line of aggreg[page]) {
            var link = baseLink;
            if (line[0].includes('<span')) {
                link += `/${line[0].replace('>', '<').split('<')[2]}#here`;
            } else {
                link += `/${line[0]}#here`;
            };

            html += `
              <div class="row">
                <div class="col-2">
                  <p><a href="${link}">${line[0]}</a></p>
                </div>
                <div class="col">
                  <p style="text-align: right">${line[1]}</p>
                </div>
                <div class="col-sm-auto">
                  <p style="text-align: center">${line[2]}</p>
                </div>
                <div class="col">
                  <p style="text-align: left">${line[3]}</p>
                </div>
              </div>
            `
        };
        // WordList
    } else if (aggreg[1][0].length === 3) {

        var wordListPage = {};

        for (item of aggreg[page]) {
            var WORD = `${item[2].replace('/', '%252F').replace('.', '%252E').replace('#', '%2523').replace("’", '%2527')}`;
            var link = baseLink.replace('WORD', WORD);

            wordListPage[`${aggreg[page].indexOf(item)}`] = `<div class="row">
                    <div class="col-1">
                      <p>${item[0]}</p>
                    </div>
                    <div class="col-6">
                      <p><a href=${link}>${item[2]}</a></p>
                    </div>
                    <div class="col-2">
                      <p>${item[1]}</p>
                    </div>
                  </div>
                  `;
        };

        var header = `<div class="row">
                      <div class="col-1">
                        <p><b>rank</b></p>
                      </div>
                      <div class="col-6">
                        <p><b>word</b></p>
                      </div>
                      <div class="col-2">
                        <p><b>frequency</b></p>
                      </div>
                    </div>
                    `;

        if (aggreg[1].length > 1) {
            html += `<div class="row">
                    <div class="col">
                      ${header}
                    </div>
                    <div class="col">
                      ${header}
                    </div>
                  </div>
                  `;

            var halfStart;
            var oddEvenLength = Object.keys(wordListPage).length % 2;
            if (oddEvenLength === 0) {
                halfStart = Object.keys(wordListPage).length / 2;
            } else if (oddEvenLength === 1) {
                halfStart = Math.ceil(Object.keys(wordListPage).length / 2);
            };

            for (var i = 0; i < halfStart; i++) {
                if (oddEvenLength === 1 && i === halfStart - 1) {
                    html += `<div class="row">
                            <div class="col">
                              ${wordListPage[i]}
                            </div>
                            <div class="col">
                            </div>
                          </div>`;
                } else {
                    html += `<div class="row">
                                  <div class="col">
                                    ${wordListPage[i]}
                                  </div>
                                  <div class="col">
                                    ${wordListPage[halfStart + i]}
                                  </div>
                                </div>`;
                };
            };

        } else {
            html += header;
            html += wordListPage[0];
        };
    };

    var renderElement = document.getElementById('render');
    renderElement.innerHTML = html;

    pageNumber1.value = page;
    pageNumber2.value = page;

    if (pageValue > 1 && first1.parentNode.classList.contains('disabled')) {
        first1.parentNode.classList.remove('disabled');
        previous1.parentNode.classList.remove('disabled');
        first1.removeAttribute('aria-disabled');
        previous1.removeAttribute('aria-disabled');
        first2.parentNode.classList.remove('disabled');
        previous2.parentNode.classList.remove('disabled');
        first2.removeAttribute('aria-disabled');
        previous2.removeAttribute('aria-disabled');
    } else if (pageValue === 1) {
        first1.parentNode.classList.add('disabled');
        previous1.parentNode.classList.add('disabled');
        first1.setAttribute('aria-disabled', 'true');
        previous1.setAttribute('aria-disabled', 'true');
        first2.parentNode.classList.add('disabled');
        previous2.parentNode.classList.add('disabled');
        first2.setAttribute('aria-disabled', 'true');
        previous2.setAttribute('aria-disabled', 'true');
    };

    if (pageValue < Object.keys(aggreg).length && last1.parentNode.classList.contains('disabled')) {
        next1.parentNode.classList.remove('disabled');
        last1.parentNode.classList.remove('disabled');
        next1.removeAttribute('aria-disabled');
        last1.removeAttribute('aria-disabled');
        next2.parentNode.classList.remove('disabled');
        last2.parentNode.classList.remove('disabled');
        next2.removeAttribute('aria-disabled');
        last2.removeAttribute('aria-disabled');
    } else if (pageValue === Object.keys(aggreg).length) {
        next1.parentNode.classList.add('disabled');
        last1.parentNode.classList.add('disabled');
        next1.setAttribute('aria-disabled', 'true');
        last1.setAttribute('aria-disabled', 'true');
        next2.parentNode.classList.add('disabled');
        last2.parentNode.classList.add('disabled');
        next2.setAttribute('aria-disabled', 'true');
        last2.setAttribute('aria-disabled', 'true');
    };
};


function sortConc(conc, options, baseLink) {

    const colors = {
        'option1': 'Gold',
        'option2': 'Blue',
        'option3': 'OrangeRed',
        'option4': 'Turquoise',
        'option5': 'Lime',
        'option6': 'DeepPink'
    };
    var concArray = [];
    const concPages = Object.keys(conc);

    for (i of concPages) {
        const verseList = conc[i].map(verse => [
            [verse[0], verse[1].trim().replace('  ', ' ').split(' '), verse[2], verse[3].trim().replace('  ', ' ').split(' '), verse[4]], null, null, null, null, null, null
        ]);
        concArray = concArray.concat(verseList);
    };

    for (option of options) {
        let optionIndex = options.indexOf(option);
        let optionColor = colors[`option${optionIndex+1}`];
        if (option !== 'None') {
            for (verse of concArray) {
                if (parseInt(option) === 0) {
                    verse[optionIndex + 1] = verse[0][4];
                    verse[0][0] = `<span class="${optionColor}">${verse[0][0]}</span>`;
                } else if (parseInt(option) === 2) {
                    verse[optionIndex + 1] = verse[0][2].toLowerCase();
                    verse[0][2] = `<span class="${optionColor}">${verse[0][2]}</span>`;
                } else {
                    try {
                        let kwicIndex;
                        if (option[0] === '3') {
                            kwicIndex = parseInt(option[1]);
                            verse[optionIndex + 1] = verse[0][3][kwicIndex].toLowerCase();
                            verse[0][3] = verse[0][3].slice(0, kwicIndex).concat(`<span class="${optionColor}">${verse[0][3][kwicIndex]}</span>`).concat(verse[0][3].slice(kwicIndex + 1));

                        } else if (option[0] === '1') {
                            kwicIndex = verse[0][1].length - parseInt(option[1]);
                            verse[optionIndex + 1] = verse[0][1][kwicIndex].toLowerCase();
                            if ((verse[0][1].length - kwicIndex) !== 1) {
                                verse[0][1] = verse[0][1].slice(0, kwicIndex).concat(`<span class="${optionColor}">${verse[0][1][kwicIndex]}</span>`).concat(verse[0][1].slice(kwicIndex + 1));
                            } else if ((verse[0][1].length - kwicIndex) === 1) {
                                verse[0][1] = verse[0][1].slice(0, kwicIndex).concat(`<span class="${optionColor}">${verse[0][1][kwicIndex]}</span>`);
                            }
                        }
                    } catch (RangeError) {
                        verse[optionIndex + 1] = ' ';
                    }
                };
            };
        };
    };

    for (var index = 0; index < concArray[0].slice(1).length; index++) {
        if (concArray[0][index + 1] !== null) {
            concArray.sort((a, b) => a[index + 1] < b[index + 1] ? -1 : a[index + 1] > b[index + 1] ? 1 : 0);
        };
    };

    const concPrePag = concArray.map(verse => [verse[0][0], verse[0][1].join(' '), verse[0][2], verse[0][3].join(' '), verse[0][4]]);

    if (concPages.length > 1) {
        let pageStep1 = 0;
        let pageStep2 = 100;
        for (i of concPages) {
            if (parseInt(i) === concPages.length) {
                conc[i] = concPrePag.slice(pageStep1);
            } else {
                conc[i] = concPrePag.slice(pageStep1, pageStep2);
                pageStep1 += 100;
                pageStep2 += 100;
            }
        };
    } else {
        conc[1] = concPrePag;
    };
    render(conc, 1, baseLink);
    return conc;
};