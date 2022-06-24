import { IHero } from "./hero";

export class NullHero implements IHero {
    id: -1;
    name: "";
    isNull: () => true

}
