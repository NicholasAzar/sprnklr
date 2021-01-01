import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { AuthService, Account } from '../auth/auth.service';
import { AppStoreService } from '../client-store/client-store.service';

@Injectable({
  providedIn: 'root'
})
export class SourcesService {
  constructor(private appStore:AppStoreService, private authService:AuthService) {

  }

  get sources():Observable<SourceAccount[]> {
    return this.appStore.getSourceAccounts();
  }

  async addAccount() {
    await this.authService.login()
    .then((response) => console.log("FINISHED LOGIN WOOO ", response))
    .then((account:Account|void) => {
      if (!account) return;
      const sourceAccount = {
        email: account.email,
        refreshToken: account.refreshToken,
        accessToken: account.accessToken,
        lastSync: null,
        active: true
      };
      this.appStore.addSourceAccount(sourceAccount);
    });
  }
}

export interface SourceAccount {
  email:string;
  refreshToken:string;
  accessToken:string;
  lastSync:string;
  active:boolean;
}
