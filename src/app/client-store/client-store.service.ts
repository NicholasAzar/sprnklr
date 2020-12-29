import { Injectable } from '@angular/core';

import { ElectronService } from '../electron/electron.service';

@Injectable({
  providedIn: 'root'
})
export class ClientStoreService {
  private store:any;

  constructor(private electronService:ElectronService) {
    if (this.electronService.isElectron) {
      const Store = window.require('electron-store');
      this.store = new Store();
    } else {
      this.store = new LocalStorageWrapper();
    }
  }

  get(key:string):string|null|unknown {
    return this.store.get(key);
  }

  set(key:string, value:string):void {
    this.store.set(key, value);
  }
}

class LocalStorageWrapper {
  get(key:string):string|null {
    return window.localStorage.getItem(key);
  }

  set(key:string, value:string):void {
    window.localStorage.setItem(key, value);
  }
}
