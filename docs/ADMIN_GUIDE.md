# Pharmacies Gabon - Admin Guide

## Getting Started

### Accessing the Admin Panel

1. Navigate to `/admin` on your domain
2. Enter your admin credentials (configured via `ADMIN_USERNAME` and `ADMIN_PASSWORD` environment secrets)
3. Click "Connexion" to access the dashboard

### Dashboard Overview

The admin dashboard provides a comprehensive view of:

- **Total Pharmacies**: Count of all registered pharmacies
- **Pending Submissions**: Location corrections, info updates, suggestions, and proposals awaiting review
- **Analytics**: View statistics for the last 7 and 30 days
- **Top Pharmacies**: Most viewed pharmacies
- **Distribution Charts**: Pharmacies by city and type

## Managing Pharmacies

### Adding a New Pharmacy

1. Click "Ajouter une pharmacie" in the dashboard
2. Fill in the required fields:
   - **Code**: Unique identifier (e.g., LBV001)
   - **Nom**: Pharmacy name
   - **Ville**: Select city from dropdown
   - **Quartier**: Neighborhood/address
3. Add optional information:
   - Phone numbers
   - Postal box (BP)
   - Operating hours
   - Services offered
   - Owner name
4. Set location category and establishment type
5. Optionally add GPS coordinates
6. Click "Enregistrer"

### Editing a Pharmacy

1. Find the pharmacy in the dashboard list
2. Click the edit icon (pencil)
3. Modify the desired fields
4. Click "Enregistrer"

### Deleting a Pharmacy

1. Find the pharmacy in the dashboard
2. Click the delete icon (trash)
3. Confirm the deletion

### Managing Duty Status (Garde)

#### Quick Toggle
- Click the duty badge to toggle on/off instantly

#### Scheduled Duty Period
1. Click "Gérer la garde" on the pharmacy
2. Select the start date
3. The system automatically sets a 7-day duty period
4. Click "Activer" to confirm

## Reviewing Submissions

### Location Submissions

When users submit GPS coordinates:

1. Go to "Localisations en attente" section
2. Review the submitted coordinates on the map
3. Compare with the current location
4. Click "Approuver" to update the pharmacy location
5. Or click "Rejeter" to decline

### Information Corrections

When users submit information updates:

1. Go to "Corrections en attente" section
2. Review the current vs. proposed value
3. Verify the information accuracy
4. Click "Approuver" to apply the change
5. Or click "Rejeter" to decline

### Suggestions

When users send suggestions:

1. Go to "Suggestions" section
2. Read the message and category
3. Click "Répondre" to provide a response
4. Or click "Archiver" to archive without response

### New Pharmacy Proposals

When users propose new pharmacies:

1. Go to "Propositions" section
2. Review all submitted information
3. Verify the pharmacy doesn't already exist
4. Click "Approuver" to create the pharmacy
5. Or click "Rejeter" to decline

## Emergency Contacts Management

### Viewing Contacts

1. Navigate to "Contacts d'urgence" in the admin menu
2. View all national and city-specific contacts
3. Contacts are sorted by ordering number

### Adding an Emergency Contact

1. Click "Ajouter un contact"
2. Select the service type:
   - Police
   - Pompiers (Fire)
   - Ambulance/SAMU
   - Hôpital (Hospital)
   - Clinique
   - SOS Médecins
   - Protection Civile
   - Autre (Other)
3. Enter contact details:
   - Label (display name)
   - Phone numbers
   - Address (optional)
   - Notes (optional)
4. Choose scope:
   - Check "National" for country-wide service
   - Or select a specific city
5. Set ordering number (lower = appears first)
6. Enable/disable with "Actif" checkbox
7. Click "Enregistrer"

### Editing/Deleting Contacts

- Click edit (pencil) or delete (trash) icons on the contact row

## Site Settings

### General Settings

Navigate to "Paramètres" to configure:

1. **Site Name**: Displayed in header and SEO
2. **Site Description**: Meta description for search engines
3. **Contact Email**: Public contact email
4. **Contact Phone**: Public contact phone

### Branding

Upload custom assets:

1. **Logo**: Site logo displayed in header
2. **Favicon**: Browser tab icon
3. **OG Image**: Image for social media sharing

To upload:
1. Click "Choose file"
2. Select an image (PNG, JPG, SVG, ICO, WEBP)
3. Click "Enregistrer"

To remove:
1. Check "Supprimer le logo/favicon/image"
2. Click "Enregistrer"

### SEO Settings

Configure search engine optimization:

1. **OG Title**: Title for social media shares
2. **OG Description**: Description for social media shares
3. **Meta Keywords**: Keywords for search engines
4. **Google Analytics ID**: Your GA tracking ID
5. **Header Code**: Custom HTML/JS for the header

## Popup Messages

### Creating a Popup

1. Navigate to "Popups" in the admin menu
2. Click "Nouveau popup"
3. Fill in:
   - **Title**: Popup header
   - **Description**: Main message content
   - **Warning Text**: Optional warning box (yellow background)
   - **Image**: Optional image
4. Configure behavior:
   - **Actif**: Enable/disable the popup
   - **Afficher une seule fois**: Show only once per user
   - **Ordre**: Display order (lower = first)
5. Click "Enregistrer"

### Managing Popups

- **Toggle**: Click the active/inactive badge to toggle status
- **Edit**: Click the edit icon
- **Delete**: Click the delete icon

### Popup Display Order

When multiple popups are active:
1. Popups display in order of their "ordering" value
2. Lower numbers appear first
3. Users can navigate between popups if multiple are active

## Analytics & Statistics

### Dashboard Statistics

The dashboard shows:

- **Total Views**: All-time pharmacy page views
- **Views Today**: Today's view count
- **Views This Week**: Current week's views
- **Views This Month**: Current month's views

### Charts

- **7-Day Trend**: Daily views for the past week
- **30-Day Trend**: Daily views for the past month
- **Distribution by City**: Pharmacy count per city
- **Distribution by Type**: Pharmacy types breakdown

### Top Pharmacies

See the 10 most-viewed pharmacies with:
- Pharmacy name
- City
- Total view count

## Best Practices

### Data Quality

1. **Verify Before Approving**: Always verify community submissions
2. **Complete Information**: Fill in all available fields when adding pharmacies
3. **GPS Accuracy**: Validate GPS coordinates using the map preview
4. **Regular Updates**: Periodically review and update pharmacy information

### Duty Management

1. **Weekly Planning**: Set up duty schedules at the start of each week
2. **Multiple Pharmacies**: Ensure adequate coverage across areas
3. **Communication**: Notify pharmacies when enabling duty status

### User Engagement

1. **Respond to Suggestions**: Regular responses encourage more contributions
2. **Quick Approvals**: Fast turnaround on valid submissions builds trust
3. **Popup Updates**: Use popups for important announcements

### Security

1. **Strong Password**: Use a secure admin password
2. **Regular Sessions**: Log out when finished
3. **Trusted Access**: Only share admin credentials with authorized personnel

## Troubleshooting

### Cannot Log In

- Verify username and password in environment secrets
- Check if `ADMIN_USERNAME` and `ADMIN_PASSWORD` are set
- Clear browser cookies and try again

### Map Not Loading

- Check internet connection
- Ensure GPS coordinates are valid numbers
- Refresh the page

### Image Upload Fails

- Verify file is an allowed type (PNG, JPG, JPEG, GIF, WEBP, SVG, ICO)
- Check file size (should be under 10MB)
- Try a different file format

### Changes Not Appearing

- Clear browser cache
- Restart the application workflow
- Check for JavaScript errors in browser console

## Support

For technical issues or feature requests, use the platform's suggestion system or contact the development team.
