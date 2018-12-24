function labelSwitcher(data_source) {
    if (data_source == '18F') {
        document.getElementById('18F').classList.add('active');
        document.getElementById('19S').classList.remove('active');
    } else {
        document.getElementById('19S').classList.add('active');
        document.getElementById('18F').classList.remove('active');
    }
}

function changesource(click_source, data_source) {
    if (data_source != click_source) {
        window.location.href = '/changesource/' + click_source;
    }

}


var tableHeaderDict = {
    1: "class_term",
    2: "class_status",
    3: "class_title",
    4: "class_number",
    5: "class_section",
    6: "class_instructor",
    7: "class_day",
    8: "class_time",
    9: "class_location",
    10: "class_isFull",
};


function CompareFunction(propertyName, order) {
    return function (obj1, obj2) {
        if (propertyName === "class_isFull") {
            var value1 = parseInt(obj1[propertyName].split("%")[0]);
            var value2 = parseInt(obj2[propertyName].split("%")[0]);
        } else {
            var value1 = obj1[propertyName];
            var value2 = obj2[propertyName];
        }
        if (order === 'asc') {
            if (value1 < value2) {
                return -1;
            } else if (value1 > value2) {
                return 1;
            } else {
                return 0;
            }
        } else if (order === 'des') {
            if (value1 > value2) {
                return -1;
            } else if (value1 < value2) {
                return 1;
            } else {
                return 0;
            }
        }

    }
}


function deltabheadericon(headerItem) {
    for (var i = 1; i < headerItem.length; i++) {
        headerItem[i].innerHTML = headerItem[i].innerHTML.replace("▲", "").replace("▼", "");
    }
}

function sortBasedOn(propertyOrder, dataSort) {
    var headerItem = document.querySelector(".table").children[1].children[0].children;
    var trs = document.querySelector(".table").lastElementChild.children;
    if (trs[0].children[propertyOrder].innerHTML >= trs[trs.length - 1].children[propertyOrder].innerHTML) {
        dataSort.sort(CompareFunction(tableHeaderDict[propertyOrder], 'asc'));
        deltabheadericon(headerItem);
        headerItem[propertyOrder].innerHTML = tableHeaderDict[propertyOrder].replace("_", " ") + "▲";
    } else {
        dataSort.sort(CompareFunction(tableHeaderDict[propertyOrder], 'des'));
        deltabheadericon(headerItem);
        headerItem[propertyOrder].innerHTML = tableHeaderDict[propertyOrder].replace("_", " ") + "▼";
    }
    for (var i = 0; i < trs.length; i++) {
        trs[i].children[0].innerHTML = i + 1;
        for (var j = 1; j < 11; j++) {
            if (j === 5) {
                var tempInnerHTML = dataSort[i][tableHeaderDict[j]];
                var tempInnerHTML_ = tempInnerHTML.split(' ')[1].split('.')[0];
                html = "<a href='https://catalog.utdallas.edu/2018/graduate/courses/%major%%tempInnerHTML_%' target='_blank'>%tempInnerHTML%</a>";
                if (tempInnerHTML.indexOf('CS') !== -1) {
                    trs[i].children[j].innerHTML = html.replace('%tempInnerHTML%', tempInnerHTML).replace('%tempInnerHTML_%', tempInnerHTML_).replace('%major%', 'cs')
                } else if (tempInnerHTML.indexOf('CE') !== -1) {
                    trs[i].children[j].innerHTML = html.replace('%tempInnerHTML%', tempInnerHTML).replace('%tempInnerHTML_%', tempInnerHTML_).replace('%major%', 'ce')
                } else if (tempInnerHTML.indexOf('EE') !== -1) {
                    trs[i].children[j].innerHTML = html.replace('%tempInnerHTML%', tempInnerHTML).replace('%tempInnerHTML_%', tempInnerHTML_).replace('%major%', 'ee')
                } else if (tempInnerHTML.indexOf('SE') !== -1) {
                    trs[i].children[j].innerHTML = html.replace('%tempInnerHTML%', tempInnerHTML).replace('%tempInnerHTML_%', tempInnerHTML_).replace('%major%', 'se')
                } else {
                    trs[i].children[j].innerHTML = tempInnerHTML;
                }

            } else if (j === 6) {
                for (var n = 0; n < dataSort[i][tableHeaderDict[j]].length; n++) {
                    var professorname = dataSort[i][tableHeaderDict[j]][n];
                    html = "<a href='/findrate/%professorname%' target='_blank' name='ratemyprofessors'>%professorname%</a>";
                    if (professorname !== '-Staff-') {
                        trs[i].children[j].innerHTML = html.replace('%professorname%', professorname).replace('%professorname%', professorname);
                    } else {
                        trs[i].children[j].innerHTML = dataSort[i][tableHeaderDict[j]];
                    }
                }
            } else {
                trs[i].children[j].innerHTML = dataSort[i][tableHeaderDict[j]];
            }
        }

    }
}