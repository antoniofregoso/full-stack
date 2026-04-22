

export function byeUpdater(previousValue, currentValue){
    let page = document.querySelector('app-page');
    
    if (previousValue.context.lang!=currentValue.context.lang||previousValue.context.theme!=currentValue.context.theme){
        page.data.context = currentValue.context;
        page.loadData();
    }
    }