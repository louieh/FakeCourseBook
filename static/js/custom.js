function labelSwitcher() {
    var data_source_now = document.querySelector(".table").children[1].children[0].children[1].textContent;
    if (data_source_now == '18F') {
        document.getElementById('18F').classList.add('active');
        document.getElementById('19S').classList.remove('active');
    } else {
        document.getElementById('19S').classList.add('active');
        document.getElementById('18F').classList.remove('active');
    }
}

function changesource(click_source) {
    var data_source_now = document.querySelector(".table").children[1].children[0].children[1].textContent;
    var headerItem = document.querySelector(".table").children[0].children[0].children;
    if (click_source !== data_source_now) {
        //window.location.href = '/changesource/' + click_source;
        fetch(`/changesource/${click_source}`)
            .then(data => {
                return data.json()
            })
            .then(data => {
                setdataForSearch(data);
                labelSwitcher();
                deltabheadericon(headerItem);
            })
            .catch(error => {
                console.log(`There is a error ${error}`)
            })
    }

}


var tabHeadDictForSearch = {
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

var tabHeadDictForGraph = {
    0: "class_section",
    1: "class_title",
};


function CompareFunction(propertyName, order) {
    return function (obj1, obj2) {
        var value1, value2;
        if (propertyName === "class_isFull") {
            value1 = parseInt(obj1[propertyName].split("%")[0]);
            value2 = parseInt(obj2[propertyName].split("%")[0]);
        } else {
            value1 = obj1[propertyName];
            value2 = obj2[propertyName];
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
    for (var i = 0; i < headerItem.length; i++) {
        headerItem[i].innerHTML = headerItem[i].innerHTML.replace("▲", "").replace("▼", "");
    }
}


function getSortedData(propertyOrder, dataOrig, tabledict) { //get sorted data and setting icon on the header of table
    var headerItem = document.querySelector(".table").children[0].children[0].children;
    var trs = document.querySelector(".table").lastElementChild.children;
    if (trs[0].children[propertyOrder].innerHTML >= trs[trs.length - 1].children[propertyOrder].innerHTML) {
        dataOrig.sort(CompareFunction(tabledict[propertyOrder], 'asc'));
        deltabheadericon(headerItem);
        headerItem[propertyOrder].innerHTML = tabledict[propertyOrder].replace("_", " ") + "▲";
    } else {
        dataOrig.sort(CompareFunction(tabledict[propertyOrder], 'des'));
        deltabheadericon(headerItem);
        headerItem[propertyOrder].innerHTML = tabledict[propertyOrder].replace("_", " ") + "▼";
    }
    return dataOrig
}


function setdataForSearch(newData) {
    var table = document.querySelector(".table");
    var i, j, n;
    if (newData.length < table.children[1].childElementCount) {
        var numOfDel = table.children[1].childElementCount - newData.length;
        for (i = 0; i < numOfDel; i++) {
            table.deleteRow(1)
        }
    } else if (newData.length > table.children[1].childElementCount) {
        var numOfAdd = newData.length - table.children[1].childElementCount;
        var el = '<tr><th></th><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>';
        for (i = 0; i < numOfAdd; i++) {
            table.children[1].insertAdjacentHTML('beforeend', el)
        }
    }

    var trs = table.lastElementChild.children;
    htmlTemplate1 = "<a href='https://catalog.utdallas.edu/2018/graduate/courses/%major%%tempInnerHTML_%' target='_blank'>%tempInnerHTML%</a>";
    htmlTemplate2 = "<a href='/findrate/%professorname%' target='_blank' name='ratemyprofessors'>%professorname%</a>";

    for (i = 0; i < trs.length; i++) {
        trs[i].children[0].innerHTML = i + 1;
        for (j = 1; j < trs[0].children.length; j++) {
            if (j === 5) {
                var tempInnerHTML = newData[i][tabHeadDictForSearch[j]];
                var tempInnerHTML_ = tempInnerHTML.split(' ')[1].split('.')[0];
                if (tempInnerHTML.indexOf('CS') !== -1) {
                    trs[i].children[j].innerHTML = htmlTemplate1.replace('%tempInnerHTML%', tempInnerHTML).replace('%tempInnerHTML_%', tempInnerHTML_).replace('%major%', 'cs')
                } else if (tempInnerHTML.indexOf('CE') !== -1) {
                    trs[i].children[j].innerHTML = htmlTemplate1.replace('%tempInnerHTML%', tempInnerHTML).replace('%tempInnerHTML_%', tempInnerHTML_).replace('%major%', 'ce')
                } else if (tempInnerHTML.indexOf('EE') !== -1) {
                    trs[i].children[j].innerHTML = htmlTemplate1.replace('%tempInnerHTML%', tempInnerHTML).replace('%tempInnerHTML_%', tempInnerHTML_).replace('%major%', 'ee')
                } else if (tempInnerHTML.indexOf('SE') !== -1) {
                    trs[i].children[j].innerHTML = htmlTemplate1.replace('%tempInnerHTML%', tempInnerHTML).replace('%tempInnerHTML_%', tempInnerHTML_).replace('%major%', 'se')
                } else {
                    trs[i].children[j].innerHTML = tempInnerHTML;
                }

            } else if (j === 6) {
                for (n = 0; n < newData[i][tabHeadDictForSearch[j]].length; n++) {
                    var professorname = newData[i][tabHeadDictForSearch[j]][n];

                    if (professorname !== '-Staff-') {
                        trs[i].children[j].innerHTML = htmlTemplate2.replace('%professorname%', professorname).replace('%professorname%', professorname);
                    } else {
                        trs[i].children[j].innerHTML = newData[i][tabHeadDictForSearch[j]];
                    }
                }
            } else {
                trs[i].children[j].innerHTML = newData[i][tabHeadDictForSearch[j]];
            }
        }

    }

}

function setdataForGraph(newData) {
    var trs = document.querySelector(".table").lastElementChild.children;
    htmlTemplate = '<a href="/graph/course/%tempInnerHTML%">%tempInnerHTML%</a>';

    for (var i = 0; i < trs.length; i++) {
        for (var j = 0; j < trs[0].children.length; j++) {
            if (j === 0) {
                trs[i].children[j].innerHTML = htmlTemplate.replace('%tempInnerHTML%', newData[i][tabHeadDictForGraph[j]]).replace('%tempInnerHTML%', newData[i][tabHeadDictForGraph[j]]);
            } else {
                trs[i].children[j].innerHTML = newData[i][tabHeadDictForGraph[j]];
            }
        }
    }
}

function sortForSearchGraph(propertyOrder, dataOrig, obj) {   //reset new sorted data for the search page
    var newData;
    if (obj === 'Search') {
        newData = getSortedData(propertyOrder, dataOrig, tabHeadDictForSearch);
        setdataForSearch(newData)
    } else if (obj === 'Graph') {
        newData = getSortedData(propertyOrder, dataOrig, tabHeadDictForGraph);
        setdataForGraph(newData)
    }

}

function test() {
    fetch('/test')
        .then(result => {
            return result.json()
        })
        .then(result => {
            console.log(result)
        })
        .catch(error => {
            console.log(`This is a error here ${error}`)
        })
}