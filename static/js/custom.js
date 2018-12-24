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


function CompareFunction(propertyName) {
    return function (obj1, obj2) {
        var value1 = obj1[propertyName];
        var value2 = obj2[propertyName];

        if (value1 < value2) {
            return -1;
        } else if (value1 > value2) {
            return 1;
        } else {
            return 0;
        }
    }
}


function sortBasedOn(propertyName, dataSort) {
    datanew.sort(CompareFunction(propertyName));
}