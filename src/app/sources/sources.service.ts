import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { AuthService } from '../auth/auth.service';
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
    await this.authService.startLogin();
  }
}

export interface SourceAccount {
  email:string;
  refreshToken:string;
  accessToken:string;
  lastSync:string;
  active:boolean;
}
