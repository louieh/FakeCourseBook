/**
 * switch active of each label
 */
function labelSwitcher() {
    var data_source_now = document.querySelector(".table").children[1].children[0].children[1].textContent;
    if (data_source_now == '20S') {
        document.getElementById('20S').classList.add('active');
        document.getElementById('19F').classList.remove('active');
    } else {
        document.getElementById('19F').classList.add('active');
        document.getElementById('20S').classList.remove('active');
    }
    setOpenStatus()
}

function setOpenStatus() {
    var table = document.querySelector(".table").lastElementChild.children;
    for (var i = 0; i < table.length; i++) {
        if (table[i].children[2].innerHTML === "Open") {
            table[i].children[2].className = 'classOpen';
            // table[i].children[2].classList.add('classOpen')
        } else if (table[i].children[2].innerHTML === "Closed") {
            table[i].children[2].className = 'classClosed';
            // table[i].children[2].classList.add('classClosed')
        }
    }
}

/**
 * change data source (19F/19S) and set data
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

var tabHeadDictForjobinfo = {
    0: "name",
    1: "company",
    2: "city",
    3: "create_time",
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
    setOpenStatus(); // reset the open or closed class for td[2]
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
function sortForSearchGraph(propertyOrder, obj, dataOrig = null) {
    var newData;
    if (!dataOrig) {
        dataOrig = getdatanow();
    }
    if (obj === 'Search') {
        newData = getSortedData(propertyOrder, dataOrig, tabHeadDictForSearch);
        setdataForSearch(newData);
    } else if (obj === 'Graph') {
        newData = getSortedData(propertyOrder, dataOrig, tabHeadDictForGraph);
        setdataForGraph(newData);
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
    return dataNowList;

}

/**
 * get rate from ratemyprofessor
 * 跨域请求
 */
function findrate(name) {
    fetch('https://search-production.ratemyprofessors.com/solr/rmp/select/?rows=20&wt=json&q=' + name + '&defType=edismax&qf=teacherfirstname_t%5E2000+teacherlastname_t%5E2000+teacherfullname_t%5E2000+autosuggest&group.limit=50')
        .then(result => {
            return result.json()
        })
        .then(result => {
            var resp_parse_list;
            resp_parse_list = result.response.docs;
            for (i = 0; i < resp_parse_list.length; i++) {
                if (resp_parse_list[i].schoolname_s === 'University of Texas at Dallas') {
                    console.log(resp_parse_list[i].pk_id)
                }
            }
        })
}


function dosomething(data) {
    data.s.map(function (html) {
        console.log("123");
        console.log(html);
        var oLi = document.createElement('li');
        oLi.innerHTML = html;
        oLi.onclick = function () {
            window.location.href = `http://www.baidu.com/s?wd=${html}`
        };
        oUl.appendChild(oLi)
    });
}

function test1(val) {
    var script = document.createElement('script');
    script.src = `https://sp0.baidu.com/5a1Fazu8AA54nxGko9WTAnF6hhy/su?wd=${val}&cb=dosomething`;
    document.body.appendChild(script);
}

/**
 * the pagination of jobinfo
 */
function jobinfo_Pagination(numnum) {
    var url_now = location.href;
    var page_pre = document.getElementById('page_pre');
    var page_next = document.getElementById('page_next');

    if (url_now.indexOf('?') === -1) {
        url_next = url_now + '?num=10'
    } else {
        num_now = url_now.match(/num=(\d+)/g);
        if (num_now == null) {
            url_next = url_now + '&num=10'
        } else {
            num_now = parseInt(num_now[0].match(/(\d+)/g)[0])
        }
        url_next = url_now.replace(('num=' + num_now), ('num=' + (num_now + numnum)));
    }
    window.history.pushState({}, 0, url_next);
    fetch('/jobinfodata?' + url_next.split('?')[1])
        .then(result => {
            return result.json()
        })
        .then(result => {
            data = result['data'];
            setdataForjobinfo(data);
            if (!result['ifnext']) {
                page_next.classList.add('disabled');
            } else {
                page_next.classList.remove('disabled');
            }
            if (!result['ifpre']) {
                page_pre.classList.add('disabled');
            } else {
                page_pre.classList.remove('disabled')
            }
        })
        .catch(error => {
            console.log(`There is a error ${error}`)
        })
}

/**
 * set data for jobinfo
 * @param newData
 */
function setdataForjobinfo(newData) {
    var trs = document.querySelector(".table").lastElementChild.children;

    for (var i = 0; i < trs.length; i++) {
        for (var j = 0; j < trs[0].children.length; j++) {
            if (tabHeadDictForjobinfo[j] === 'create_time')
                dataTemp = newData[i][tabHeadDictForjobinfo[j]].split(' ')[0];
            else {
                dataTemp = newData[i][tabHeadDictForjobinfo[j]]
            }
            trs[i].children[j].innerHTML = dataTemp;
        }
    }
}