export interface IHero {
    id: number;
    name: string;

    isNull() : boolean
}

export class Hero implements IHero {
    id: number;
    name: string;
    isNull: () => false;
    
}
