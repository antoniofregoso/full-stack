import config from './.env/conf.json';
import { store, persistor } from './app/store/store';
import { setSession } from './app/store/slices/contextSlice';
import { generateSessionToken, loading, whithAnimations } from "@customerjourney/cj-core"
import 'animate.css';
import '@customerjourney/cj-core/src/pageloader.css';
import { App } from './App';
/**
 * Set Loading element before app run
 */
loading({color:"is-dark", direction:"is-right-to-left"});

let isRehydrated = false;

function startApp() {
    // If you haven't rehydrated, we're leaving.
    if (!isRehydrated) {
        console.warn('Attention! Rehydration is not complete. Waiting...');
        return;
    }

    console.log('✅ Complete rehydration. Data is ready.');

    const currentState = store.getState();
    const session  = currentState?.context?.session;
    if(!session){
        const newSession = generateSessionToken(32);
        store.dispatch(setSession(newSession));
    }
    if(currentState?.context?.theme){
        document.documentElement.setAttribute('data-theme', currentState.context.theme);
    }
    
    App.run();
}

const unsubscribe = persistor.subscribe(() => {

    const persistorState = persistor.getState();

    if (persistorState.bootstrapped && !isRehydrated) {
        isRehydrated = true;
        unsubscribe(); // Stop listening to avoid unnecessary future executions
        startApp();    // Launch the main application!
        whithAnimations();  //Enable animations
    }
});



