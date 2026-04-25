import { AppPage, PageHeader, PageFooter } from "@customerjourney/cj-core";
import { HeroBanner } from "@customerjourney/cj-components";
import { setLanguaje, setTheme } from "../store/slices/contextSlice"
import { store } from "../store/store";
import { notFoundUpdater } from "./updaters/notFoundUpdater";
import data from "../data/404.json";

export function notFound(req, router) {

    let template = `
    <page-header id="header"></page-header>
    <hero-banner id="hero"></hero-banner>
    <page-footer id="footer"></page-footer>
    `;

    let currentState = store.getState();
    data.context = currentState.context;
    let page = new AppPage(data, template);

    const pageEvents = {
        handleEvent: (e) => {
            switch (e.type) {
                case 'user:select-lang':
                    store.dispatch(setLanguaje(e.detail));
                    break;
                case 'user:select-theme':
                    store.dispatch(setTheme(e.detail));
                    break;
            }
        }
    }

    function handleChange() {
        let previousState = currentState;
        currentState = store.getState();
        if (previousState !== currentState) {
            notFoundUpdater(previousState, currentState);
        }
    }

    page.setEvents(pageEvents);

    store.subscribe(handleChange);
}