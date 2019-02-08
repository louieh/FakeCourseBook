/**
 * switch active of each label
 */
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

/**
 * change data source (18F/19S) and set data
 * @param click_source
 */
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

/**
 * sort function for the sort data function
 * @param propertyName
 * @param order
 * @returns {Function}
 * @constructor
 */
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

/**
 * delete ▲▼
 * @param headerItem
 */
function deltabheadericon(headerItem) {
    for (var i = 0; i < headerItem.length; i++) {
        headerItem[i].innerHTML = headerItem[i].innerHTML.replace("▲", "").replace("▼", "");
    }
}

/**
 * get sorted data and setting icon on the header of table
 * @param propertyOrder
 * @param dataOrig
 * @param tabledict
 * @returns {*}
 */
function getSortedData(propertyOrder, dataOrig, tabledict) {
    var headerItem = document.querySelector(".table").children[0].children[0].children;
    var trs = document.querySelector(".table").lastElementChild.children;
    var text1 = trs[0].children[propertyOrder].innerHTML;
    var text2 = trs[trs.length - 1].children[propertyOrder].innerHTML;
    if (text1.indexOf("%") != -1) {
        text1 = parseInt(text1.split("%")[0]);
        text2 = parseInt(text2.split("%")[0]);
    }
    if (text1 >= text2) {
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

/**
 * set data for search view
 * @param newData
 */
function setdataForSearch(newData) {

    // adjust the number of td
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
                var instructorNum = newData[i][tabHeadDictForSearch[j]].length, text;
                trs[i].children[j].innerHTML = "";
                for (n = 0; n < instructorNum; n++) {
                    var professorname = newData[i][tabHeadDictForSearch[j]][n];
                    if (professorname !== '-Staff-') {
                        text = htmlTemplate2.replace('%professorname%', professorname).replace('%professorname%', professorname);
                    } else {
                        text = newData[i][tabHeadDictForSearch[j]];
                    }
                    if (instructorNum > 1) {
                        trs[i].children[j].innerHTML += text + ";";
                    } else {
                        trs[i].children[j].innerHTML += text;
                    }
                }
            } else {
                trs[i].children[j].innerHTML = newData[i][tabHeadDictForSearch[j]];
            }
        }

    }

}

/**
 * set data for the graph view
 * @param newData
 */
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

/**
 * reset new sorted data for the search page
 * @param propertyOrder
 * @param obj
 */
function sortForSearchGraph(propertyOrder, obj) {
    var newData;
    dataOrig = getdatanow();
    if (obj === 'Search') {
        newData = getSortedData(propertyOrder, dataOrig, tabHeadDictForSearch);
        //console.log(newData);
        setdataForSearch(newData)
    } else if (obj === 'Graph') {
        newData = getSortedData(propertyOrder, dataOrig, tabHeadDictForGraph);
        setdataForGraph(newData)
    }

}

/**
 * get current data
 * @returns {Array}
 */
function getdatanow() {
    var table = document.querySelector(".table");
    var dataNowList = [];
    for (var i = 1; i < table.rows.length; i++) {
        var rowDict = {};
        for (var j = 1; j < table.rows[i].cells.length; j++) {
            if (tabHeadDictForSearch[j] === "class_instructor") {
                var forList = table.rows[i].cells[j].innerText.split(";");
                var retuList = [];
                for (eachIndex in forList) {
                    if (forList[eachIndex]) {
                        retuList[eachIndex] = forList[eachIndex].replace(/^\s+|\s+$/g, "");
                    }
                }
                rowDict[tabHeadDictForSearch[j]] = retuList;
            } else {
                rowDict[tabHeadDictForSearch[j]] = table.rows[i].cells[j].innerText;
            }
        }
        dataNowList[i - 1] = rowDict;
    }
    //console.log(dataNowList);
    return dataNowList;

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