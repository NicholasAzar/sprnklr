import React, {Component} from 'react'
import axios from 'axios'
import Cookies from 'universal-cookie';

const cookies = new Cookies();

export default class Dashboard extends Component {
    state = {
        linked_accounts: [],
        photos: []
    }
    componentDidMount() {
        this.getData();
    }

    async getData() {
        const accounts_response = await axios.get('/api/list-accounts'); 
        console.log("linked accounts? ", accounts_response.data);
        this.setState({linked_accounts: accounts_response.data});

        const photos_response = await axios.get('/api/list-photos');
        console.log('photos response: ', photos_response);
        this.setState({photos: photos_response.data})
    }

    async setAccountAsPrimary(email) {
        console.log("Setting " + email + " as primary.")
        const set_response = await axios.post('/api/set-primary-account', {'tpy_user_id': email}, {headers: {'Content-Type': 'application/json'}})
        if (set_response.status >= 200 && set_response.status < 300) {
            const accounts_response = await axios.get('/api/list-accounts');
            this.setState({linked_accounts: accounts_response.data})
        }
    }

    render() {
        return (
            <>
                <h1>Dashboard</h1>
                <p>Logged in as: {cookies.get('user_id')} {cookies.get('acc_type')}</p>
                <h2>Linked Accounts</h2>
                <ul style={{listStyle: "none"}}>
                    {this.state.linked_accounts.map((account) => (
                        <li key={account[0]}>
                            Email: {account[0]}, Type: {account[1]}, Primary: {account[3]}
                            {/* only display set account primary if account is not currently primary.*/}
                            { account[3] === 0 &&
                                <button onClick={() => this.setAccountAsPrimary(account[0])}>Set as primary</button>
                            }
                        </li>
                    ))}
                </ul>

                <h2>Photos</h2>
                <div style={{display: 'flex', flexWrap: 'wrap'}}>
                    {this.state.photos.map((photo) => (
                        <img src={photo.baseUrl} style={{margin: '10px', flex: '1 0 0', height: '200px', objectFit: 'contain'}} key={photo.id}></img>
                    ))}
                    
                </div>
            </>
        )
    }
}


