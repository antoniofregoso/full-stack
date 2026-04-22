import { AppPage, PageHeader, PageFooter } from "@customerjourney/cj-core";
import { HeroBanner, ImageText, LevelCentered, CardsList, ModalBox } from "@customerjourney/cj-components";
import { MultiSlider } from "@customerjourney/cj-sliders";
import { setStage, setScrollStopping } from "../store/slices/homeSlice";
import { setLanguaje, setTheme } from "../store/slices/contextSlice"
import { store } from "../store/store";
import { homeUpdater } from "./updaters/homeUpdater";
/**
 * home.json data describe the content of the page, design and animations
 * @type {object}
 */
import data from "../data/home.json";
/**
 * Declare callback funtion for home page
 * @param {object} req 
 * @param {object} router 
 */
export function home(req, router) {
    /**
     * Template for the page
     */
    let template =/*html*/`
    <page-header id="header"></page-header>
    <page-footer id="footer"></page-footer>
    <modal-box id="message"></modal-box>
    `;
    /**
     * current state of the app
     * @type {object}
     */
    let currentState = store.getState();
    /**
     * dispath start stage
     */
    store.dispatch(setStage('start'));
    /**
     * Add context to the data
     */
    data.context = currentState.context;
    /**
     * Page object created with the data and the template
     */
    let page = new AppPage(data, template);

    /**
     * event handlers for the page
     */
    const pageEvents = {
        handleEvent: (e) => {
            console.log("Event received in page:", e.type, e.detail);
            switch (e.type) {
                /* User change language or theme */
                case 'user:select-lang':
                    store.dispatch(setLanguaje(e.detail));
                    break;
                case 'user:select-theme':
                    store.dispatch(setTheme(e.detail));
                    break;
                case 'app-click':
                    switch (e.detail.source) {
                        case "attention-button":
                            store.dispatch(setStage('attention/click'));
                            break;
                    }
                    break;
                case 'cta-click':
                    console.log("User clicked CTA button", e.detail.source);
                    //store.dispatch(setStage('conversion/click'));
                    break;
            }
        }

    }
    /**
      * Handle state changes in the store
      */
    function handleChange() {
        let previousState = currentState;
        currentState = store.getState();
        if (previousState !== currentState) {
            homeUpdater(previousState, currentState);
        }
    }
    /**
     * set event handlers for the page
     */
    page.setEvents(pageEvents);
    /**
     * Suscribe to the store to listen for state changes
     */
    store.subscribe(handleChange);

}