# solax-cloud-api-notifier

### Steps to run Solax Cloud API Notifier project

Create virtual environment and activate:
```zsh
make create-env && ./solax-cloud-notifier/bin/activate
```

Install dependencies:
```zsh
make install
```

Build translations:
```zsh
make build-tranlsations
```

---

#### Run Telegram notifications bot

1. Run Telegram subscriber:
  ```zsh
    make telegram-subscriber
  ```
  Results:

  <img width="641" height="108" alt="image" src="https://github.com/user-attachments/assets/3b92bd26-ed92-424f-834d-a2d7cf36467f" />
  <img width="363" height="104" alt="image" src="https://github.com/user-attachments/assets/dda7c392-733b-4ca6-8866-ea19680f38b2" />

  #### subscribers.json will be created with the following content:
  <img width="249" height="60" alt="image" src="https://github.com/user-attachments/assets/224fb584-c0a4-4a2d-b2a8-1573a22fa403" />


---

2. Run Telegram notifier
  ```zsh
    make telegram-notify
  ```
  Results:
  
  <img width="618" height="76" alt="image" src="https://github.com/user-attachments/assets/4e691fc7-db15-443e-b41d-022e58372e6a" />
  <img width="381" height="112" alt="image" src="https://github.com/user-attachments/assets/4e469ace-1086-423f-8f9d-f7138cde1dd3" />
  
  #### solax_state_<CURRENT_YEAR>.json will be created with the following content:
  <img width="834" height="436" alt="image" src="https://github.com/user-attachments/assets/6b406667-d154-492f-8a74-0c84c47d6bf1" />







