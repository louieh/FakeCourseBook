/**
 * search page init function
 */
function search_page_init() {
    labelSwitcher();
    change_search_tool_base_status();
    collapse_search_tool();
    add_shadow();
    semester_switcher();
}

/**
 * for search page
 * semester switcher event
 */
function semester_switcher() {
    $('#20S').on('click', function () {
        changesource('20S')
    });
    $('#19F').on('click', function () {
        changesource('19F')
    });
}

/**
 * for search page
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

/**
 * for search page
 * add shadow class for each row
 */
function add_shadow() {
    $('#search-page-table').on('dblclick', 'tr', function () {
        var shadow_class_name = 'font-weight-bold shadow-lg p-3 mb-5 bg-white rounded';
        $(this).toggleClass(shadow_class_name);
    })
}

/**
 * for search page
 * switch active of each label
 */
function labelSwitcher() {
    var term1 = '20S';
    var term2 = '19F';
    var data_source_now = document.querySelector(".table").children[1].children[0].children[1].textContent;
    if (data_source_now === term1) {
        document.getElementById(term1).classList.add('active');
        document.getElementById(term2).classList.remove('active');
    } else {
        document.getElementById(term2).classList.add('active');
        document.getElementById(term1).classList.remove('active');
    }
    setOpenStatus()
}

/**
 * for search page
 * set open status class
 */
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
 * for search page
 * collapse search tool function and switch icon
 */
function collapse_search_tool() {
    $('#p-search-tool').on('click', function () {
        if ($(this).find('[data-fa-i2svg]').hasClass('fa-chevron-circle-down')) {
            $(this).find('[data-fa-i2svg]').removeClass('fa-chevron-circle-down').addClass('fa-chevron-circle-up');
            $('#search-tool').collapse('toggle');
            get_search_tool_status(true);
        } else {
            $(this).find('[data-fa-i2svg]').removeClass('fa-chevron-circle-up').addClass('fa-chevron-circle-down');
            $('#search-tool').collapse('toggle');
            get_search_tool_status(false);
        }
    });
}

/**
 * for search page
 * change search tool based on status from session
 * call this function all the time
 */
function change_search_tool_base_status() {
    get_search_tool_status().then(function (status) {
        if ((status === true && $('#p-search-tool').find('[data-fa-i2svg]').hasClass('fa-chevron-circle-up')) || (status === false && $('#p-search-tool').find('[data-fa-i2svg]').hasClass('fa-chevron-circle-down'))) {
        } else {
            if (status === true) {
                $('#search-tool').collapse('show');
                $('#p-search-tool').find('[data-fa-i2svg]').removeClass('fa-chevron-circle-down').addClass('fa-chevron-circle-up');
            } else {
                $('#search-tool').collapse('hide');
                $('#p-search-tool').find('[data-fa-i2svg]').addClass('fa-chevron-circle-down').removeClass('fa-chevron-circle-up');
            }
        }
    });
}

/**
 * for search page
 * get and change the search tool status from session
 * @param status
 * @returns {Promise<any>}
 */
function get_search_tool_status(status) {
    if (typeof (status) == "undefined") {
        return fetch(`/get_put_search_tool_status`)
            .then(data => {
                return data.json()
            })
            .then(data => {
                return data["status"];
            })
            .catch(error => {
                console.log(`There is a error ${error}`)
            });
    } else {
        fetch(`/get_put_search_tool_status/${status}`)
            .then(data => {
                return data.json()
            })
            .then(data => {
                console.log("put search tool status")
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
 * For sorting
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
 * For sorting
 * delete ▲▼
 * @param headerItem
 */
function deltabheadericon(headerItem) {
    for (var i = 0; i < headerItem.length; i++) {
        headerItem[i].innerHTML = headerItem[i].innerHTML.replace("▲", "").replace("▼", "");
    }
}

/**
 * For sorting
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
 * for search page and sorting of search page
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
    htmlTemplate1 = "<a href='/course/%section_%' target='_blank'>%section%</a>";
    htmlTemplate2 = "<a href='/professor/%professorname%' target='_blank'>%professorname%</a>";

    for (i = 0; i < trs.length; i++) {
        trs[i].children[0].innerHTML = i + 1;
        for (j = 1; j < trs[0].children.length; j++) {
            if (j === 5) {
                var tempInnerHTML = newData[i][tabHeadDictForSearch[j]];
                var tempInnerHTML_ = tempInnerHTML.split('.')[0];
                trs[i].children[j].innerHTML = htmlTemplate1.replace('%section_%', tempInnerHTML_).replace('%section%', tempInnerHTML)

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
 * For sorting of graph page
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
 * For sorting
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
 * For sorting
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
 * draw tree chart for professor and course
 * @param datasource
 * @param ifprofessor
 */
function from_left_to_right_tree(datasource, ifprofessor, graph_id) {
    var myChart = echarts.init(document.getElementById(graph_id));
    myChart.showLoading();
    myChart.hideLoading();

    var count = 0;
    datasource['children'].forEach(function (item) {
        count += item['children'].length;
    });
    if (count > 40) {  // 当有大于40个节点是收起部分节点，40写死
        echarts.util.each(datasource['children'], function (datum, index) {
            (index + 1) % 2 === 0 && (datum.collapsed = true);
        })
    }

    myChart.setOption(option = {
        tooltip: {
            trigger: 'item',
            triggerOn: 'mousemove'
        },
        series: [
            {
                type: 'tree',
                data: [datasource],
                top: '1%',
                left: '9%',
                bottom: '1%',
                right: '30%',
                symbolSize: 7,
                label: {
                    normal: {
                        position: 'left',
                        verticalAlign: 'middle',
                        align: 'right',
                        fontSize: 12
                    }
                },
                leaves: {
                    label: {
                        normal: {
                            position: 'right',
                            verticalAlign: 'middle',
                            align: 'left'
                        }
                    }
                },
                expandAndCollapse: true,
                animationDuration: 550,
                animationDurationUpdate: 750
            }
        ]
    });
    myChart.on('click', function (params) {
        if (ifprofessor === 1) {
            if (params.value)
                window.open('/graph/course/CS ' + encodeURIComponent(params.value));
        } else if (ifprofessor === 0) {
            if (params.value)
                window.open('/graph/professor/' + encodeURIComponent(params.value));
        }
    });
}

/**
 * draw line chart for speed
 * @param x_data
 * @param y_data
 * @param graph_id
 */
function basic_line_chart(x_data, y_data, graph_id) {
    var myChart = echarts.init(document.getElementById(graph_id));
    myChart.showLoading();
    myChart.hideLoading();

    option = {
        xAxis: {
            type: 'category',
            data: x_data,
        },
        yAxis: {
            type: 'value'
        },
        dataZoom: [
            {
                type: 'slider',
                start: 10,
                end: 60
            }
        ],
        series: [{
            data: y_data,
            type: 'line'
        }]
    };
    if (option && typeof option === "object") {
        myChart.setOption(option, true);
    }
}

/**
 * pie chart for grade graph
 * @param grades
 * @param graph_id
 */
function pie_doughnut_chart(grades, graph_id) {
    var dom = document.getElementById(graph_id);
    var myChart = echarts.init(dom);
    var app = {};
    option = null;

    var grade_color = {
        "A": "#009900",
        "A-": "#00cc00",
        "B+": "#ffcc00",
        "B": "#ff9900",
        "B-": "#ff6600",
        "C+": "#ff3300",
        "C": "#cc3300",
        "F": "#cc0000",
        "W": "#BDBDBD",
    };
    var series_data = new Array();
    for (var key in grades) {
        var temp = {
            value: grades[key], name: key, itemStyle: {
                color: grade_color[key]
            }
        };
        series_data.push(temp);
    }

    option = {
        tooltip: {
            trigger: 'item',
            formatter: "{a} <br/>{b}: {c} ({d}%)"
        },
        legend: {
            orient: 'vertical',
            x: 'left',
            data: Object.keys(grades)
        },
        series: [
            {
                name: 'Grades',
                type: 'pie',
                radius: ['40%', '60%'],
                avoidLabelOverlap: false,
                label: {
                    normal: {
                        show: false,
                        position: 'center'
                    },
                    emphasis: {
                        show: true,
                        textStyle: {
                            fontSize: '30',
                            fontWeight: 'bold'
                        }
                    }
                },
                labelLine: {
                    normal: {
                        show: false
                    }
                },
                data: series_data
                //     [
                //     {value: 335, name: '直接访问'},
                //     {value: 310, name: '邮件营销'},
                //     {value: 234, name: '联盟广告'},
                //     {value: 135, name: '视频广告'},
                //     {value: 1548, name: '搜索引擎'}
                // ]
            }
        ]
    };

    if (option && typeof option === "object") {
        myChart.setOption(option, true);
    }
}

/**
 * For comment page
 * generate comment section
 * @param data_title
 * @param data_isso_id
 */
function comment_section(data_title, data_isso_id) {
    var parent = document.getElementById("comment-section");
    if (parent.firstChild != null) {
        while (parent.firstChild) {
            parent.removeChild(parent.firstChild);
        }
    }

    var section = document.createElement("section");
    var attr_id = document.createAttribute("id");
    attr_id.value = "isso-thread";
    var attr_data_title = document.createAttribute("data-title");
    attr_data_title.value = data_title;
    var attr_data_isso_id = document.createAttribute("data-isso-id");
    attr_data_isso_id.value = data_isso_id;
    section.setAttributeNode(attr_id);
    section.setAttributeNode(attr_data_isso_id);
    section.setAttributeNode(attr_data_title);
    parent.appendChild(section);
    window.Isso.init();
    window.Isso.fetchComments();
}

/**
 * For course page
 * use to fill course description div
 * @param course_section
 */
function fill_course_description(course_section) {
    if (course_section != null) {
        fetch(`/get_course_description/${course_section}`)
            .then(data => {
                return data.json()
            })
            .then(data => {
                var description_div = document.getElementById("course-description");
                description_div.innerText = data;
                var spinner = document.getElementById("spinner-grow");
                spinner.setAttribute("hidden", "");
            })
            .catch(error => {
                console.log(`There is a error ${error}`)
            })
    }
}

/**
 * For course page and professor page
 * sroll for side navbar
 */
function side_nav_init() {
    $('#nav-description').on('click', function () {
        $('#description')[0].scrollIntoView({behavior: "smooth"})
    });
    $('#nav-professors').on('click', function () {
        $('#professors')[0].scrollIntoView({behavior: "smooth"})
    });
    $('#nav-status').on('click', function () {
        $('#status')[0].scrollIntoView({behavior: "smooth"})
    });
    $('#nav-grades').on('click', function () {
        $('#grades')[0].scrollIntoView({behavior: "smooth"})
    });
    $('#nav-comments').on('click', function () {
        $('#comments')[0].scrollIntoView({behavior: "smooth"})
    });
    $('#nav-links').on('click', function () {
        $('#links')[0].scrollIntoView({behavior: "smooth"})
    });
    $('#nav-courses').on('click', function () {
        $('#courses')[0].scrollIntoView({behavior: "smooth"})
    })
}

/**
 * For course page
 * course grade icon init function
 * bind click event: change icon and collapse status
 * course grade collapse close function: close some sections
 * @param grade_data_dict
 */
function course_grade_icon_init_collapse_close(grade_data_dict) {
    for (var each_professor in grade_data_dict) {
        var term_section_dict_list = grade_data_dict[each_professor];
        term_section_dict_list.forEach(function (item) {
            var each_term_section = Object.keys(item)[0];
            var graph_id = (each_professor + each_term_section)
                .replace(/\s+/g, "")
                .replace(/-/g, "")
                .split('|').join('')
                .split(',').join('');
            $('#p-' + graph_id).on('click', {graph_id: graph_id}, function (event) { //循环绑定事件传参
                $(this)
                    .find('[data-fa-i2svg]')
                    .toggleClass('fa-eye')
                    .toggleClass('fa-eye-slash');
                $('#' + event.data.graph_id).collapse('toggle');
            });
        });
    }

    // for (var each_professor in grade_data_dict) {
    //     var term_section_dict_list = grade_data_dict[each_professor];
    //     if (term_section_dict_list.length > 1) {
    //         for (var i = 1; i < term_section_dict_list.length; i++) {
    //             var each_term_section = Object.keys(term_section_dict_list[i]);
    //             var graph_id = (each_professor + each_term_section)
    //                 .replace(/\s+/g, "")
    //                 .replace(/-/g, "")
    //                 .split('|').join('')
    //                 .split(',').join('');
    //             $('#' + graph_id).collapse('toggle');
    //         }
    //     }
    // }
}

/**
 * For professor page
 * professor introduction buttom
 * @param professor_name
 */
function custom_search_button(professor_name) {
    if (professor_name != null) {
        fetch(`/custom_search_fun/${professor_name}`)
            .then(data => {
                return data.json()
            })
            .then(data => {
                if (data.hasOwnProperty("link")) {
                    var link = data["link"];
                    window.open(link);
                } else {
                    console.log(data["error"]);
                    window.open("https://www.google.com/search?q=" + professor_name);
                }
            })
            .catch(error => {
                console.log(`There is a error ${error}`)
            })
    }
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

