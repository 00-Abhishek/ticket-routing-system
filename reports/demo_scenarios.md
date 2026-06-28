# Demo Scenarios

These scenarios are prepared for the final NTCC project demo.

| # | Input Ticket | Expected Category | Expected Entities | Expected Priority | Expected Routing Team |
| ---: | --- | --- | --- | --- | --- |
| 1 | Unable to login to Outlook on my laptop | Access | SOFTWARE: Outlook; DEVICE: laptop | High | Access Management Team |
| 2 | Production server is down in the data center with HTTP 500 | Hardware | SYSTEM: server; LOCATION: data center; ERROR_CODE: HTTP 500 | Critical | Hardware Team |
| 3 | Need admin rights to install Visual Studio on Windows | Administrative rights | SOFTWARE: Visual Studio, Windows | Medium | System Administration Team |
| 4 | New starter needs payroll and HR portal setup | HR Support | SYSTEM: payroll | Medium | HR Team |
| 5 | Please increase shared mailbox storage | Storage | SYSTEM: mailbox, storage | Medium | Storage Team |
| 6 | Purchase request for headset and wireless mouse | Purchase | DEVICE: headset, mouse | Medium | Procurement Team |
| 7 | Create new internal project code for Oracle migration | Internal Project | SOFTWARE: Oracle | Medium | Internal Projects Team |
| 8 | Need documentation for meeting room monitor | Miscellaneous | LOCATION: meeting room; DEVICE: monitor | Low | Service Desk Team |
| 9 | VPN not working for remote user | Access | LOCATION: remote | High | Access Management Team |
| 10 | Printer is not working on the finance floor | Hardware | DEVICE: printer; LOCATION: floor | Medium | Hardware Team |

## Demo Flow

1. Start FastAPI.
2. Start Streamlit.
3. Open dashboard.
4. Paste one scenario.
5. Click `Analyze Ticket`.
6. Show category, confidence, entities, priority, routing team.
7. Open `/history` to show persistence.
8. Open `/analytics` to show persisted analytics.

