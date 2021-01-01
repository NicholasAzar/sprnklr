import { Target } from '@angular/compiler';
import { Injectable } from '@angular/core';
import { ReplaySubject, Observable } from 'rxjs';

import { ElectronService } from '../electron/electron.service';
import { SourceAccount } from '../sources/sources.service';
import { TargetAccount } from '../targets/targets.service';

@Injectable({
  providedIn: 'root'
})
export class AppStoreService {

  private sourceAccounts:SourceAccount[] = [];
  private sourceAccountsSubject = new ReplaySubject<SourceAccount[]>();

  private targetAccounts:TargetAccount[] = [];
  private targetAccountsSubject = new ReplaySubject<TargetAccount[]>();

  constructor(private clientStore:ClientStoreService) {
    const sourceAccounts = this.clientStore.get('sourceAccounts');
    const targetAccounts = this.clientStore.get('targetAccounts');

    if (sourceAccounts && sourceAccounts.length > 0) {
      this.sourceAccounts = sourceAccounts;
      this.sourceAccountsSubject.next(this.sourceAccounts);
    }

    if (targetAccounts && targetAccounts.length > 0) {
      this.targetAccounts = targetAccounts;
      this.targetAccountsSubject.next(this.targetAccounts);
    }
  }

  getSourceAccount(email:string):SourceAccount|null {
    const matchingAccounts = this.sourceAccounts.filter((sourceAccount:SourceAccount) => sourceAccount.email === email);
    if (matchingAccounts.length == 0) return null;
    return matchingAccounts[0];
  }

  getSourceAccounts():Observable<SourceAccount[]> {
    return this.sourceAccountsSubject;
  }

  getTargetAccounts():Observable<TargetAccount[]> {
    return this.targetAccountsSubject;
  }

  replaceSourceAccount(sourceAccount:SourceAccount) {
    let index:number = null;

    this.sourceAccounts = this.sourceAccounts.filter((account, i, arr) => {
      if (account.email === sourceAccount.email) {
        index = i;
        return false;
      }
      return true;
    });
    if (index !== null) {
      this.sourceAccounts.splice(0, index, sourceAccount);
    } else {
      this.sourceAccounts.push(sourceAccount);
    }
    this.persistSourceAccounts();
  }

  addSourceAccount(sourceAccount:SourceAccount) {
    this.sourceAccounts.push(sourceAccount);
    this.persistSourceAccounts();
    this.sourceAccountsSubject.next(this.sourceAccounts);
  }

  clearAllSourceAccounts() {
    this.sourceAccounts = [];
    this.persistSourceAccounts();
    this.sourceAccountsSubject.next(this.sourceAccounts);
  }

  addTargetAccount(targetAccount:TargetAccount) {
    this.targetAccounts.push(targetAccount);
    this.persistTargetAccounts();
    this.targetAccountsSubject.next(this.targetAccounts);
  }

  clearAllTargetAccounts() {
    this.targetAccounts = [];
    this.persistTargetAccounts();
    this.targetAccountsSubject.next(this.targetAccounts);
  }

  removeSourceAccount(email:string) {
    this.sourceAccounts = this.sourceAccounts.filter((account) => {
      return account.email !== email;
    });
    this.persistSourceAccounts();
  }

  private persistSourceAccounts() {
    this.clientStore.set('sourceAccounts', this.sourceAccounts);
  }

  private persistTargetAccounts() {
    this.clientStore.set('targetAccounts', this.targetAccounts);
  }
}


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

  get(key:string):any {
    return this.store.get(key) as string;
  }

  set(key:string, value:any):void {
    this.store.set(key, value);
  }
}

class LocalStorageWrapper {
  get(key:string):any {
    return window.localStorage.getItem(key);
  }

  set(key:string, value:any):void {
    window.localStorage.setItem(key, value);
  }
}
