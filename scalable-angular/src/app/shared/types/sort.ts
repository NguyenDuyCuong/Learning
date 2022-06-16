import {SortOrder} from '@app/app.constants';

export interface Sort {
    field: string;
    order?: SortOrder;
}
