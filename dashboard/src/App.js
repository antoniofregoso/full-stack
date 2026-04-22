import { Router } from "@customerjourney/cj-router";
import { home, bye, notFound } from "./app/pages";

export const App = new Router();
App.on('/', home);
App.on('/bye', bye);
App.onNotFound(notFound);