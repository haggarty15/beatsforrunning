# TICKET-007: Migrate Hosting to Google Cloud / Firebase

## Description

Migrate the deployment and hosting from AWS Amplify to a Google-based service (e.g., Firebase Hosting or Google Cloud Run). The service should support CI/CD from GitHub, custom domains (`pacebeats.run`), and ideally provide a way to host both the static frontend and the Flask backend.

## Acceptance Criteria

- [ ] Select appropriate Google Cloud service (Firebase Hosting for frontend, Cloud Run for backend or combined)
- [ ] Configure CI/CD pipeline (e.g., GitHub Actions) to deploy `main` and `develop` branches
- [ ] Set up custom domain configuration for `pacebeats.run`
- [ ] Ensure SSL/HTTPS is correctly configured
- [ ] Validate that the frontend can communicate with the backend in the new environment
- [ ] Documentation updated with new deployment instructions
