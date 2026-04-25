import { store } from "../../store/store";
import { setSectionTracking, setEscapeAttempt } from "../../store/slices/homeSlice";
/**
 * Manage changes in the home page state
 * @param {object} previousState 
 * @param {objecy} currentState 
 */
export function homeUpdater(previousState, currentState){
    /**
     * Page instance
     * @type {object}
     */
    let page = document.querySelector('app-page');
    /**
     * If there are changes in language or theme, update the context and reload data.
     * If there are changes in the home stage, update the appoinment component accordingly.
     */
    if (previousState.context.lang!=currentState.context.lang||previousState.context.theme!=currentState.context.theme){
        page.data.context = currentState.context;
        page.loadData();
    }else if(previousState.home.stage!=currentState.home.stage){
        console.log("Home stage changed to: ", currentState.home.stage);
        let track = currentState.home.scrollStopping;
        let payload = {};
        switch (currentState.home.stage){
            case 'atention/click':
                document.getElementById("action").scrollIntoView({ behavior: "smooth"});
                break;
            case 'attention/viewed':
                payload = page.setSectionViewed('attention',track.sections.attention);
                store.dispatch(setSectionTracking(payload));
                break;
            case 'interest/viewed':
                payload = page.setSectionViewed('interest',track.sections.interest);
                store.dispatch(setSectionTracking(payload));
                break;
            case 'desire/viewed':
                payload = page.setSectionViewed('desire',track.sections.desire);
                store.dispatch(setSectionTracking(payload));
                break;
            case 'action/viewed':
                payload = page.setSectionViewed('action',track.sections.action);
                store.dispatch(setSectionTracking(payload));
                break;
            case 'attention/unviewed':
                payloasd = page.setSectionUnviewed('attention',track.sections.attention);
                store.dispatch(setSectionTracking(payload));
                break;
            case 'interest/unviewed':
                payload = page.setSectionUnviewed('interest',track.sections.interest);
                store.dispatch(setSectionTracking(payload));
                break;
            case 'desire/unviewed':
                payload = page.setSectionUnviewed('desire',track.sections.desire);
                store.dispatch(setSectionTracking(payload));
                break;
            case 'action/unviewed':
                payload = page.setSectionUnviewed('action',track.sections.action);
                store.dispatch(setSectionTracking(payload));
                break;                
            case 'escape':
                console.log("User is trying to leave the app", track.page.leavingapp);
                let leavingApp = track.page.leavingapp + 1;
                console.log("Escape attempts: ", leavingApp);
                store.dispatch(setEscapeAttempt(leavingApp));
                if (leavingApp===1){
                    document.getElementById("message").setAttribute("active", "")
                }
                break;
            case 'quit':
                break;
        }
    }
}

