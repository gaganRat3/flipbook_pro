# Event Management Guide

This document explains how the event management system has been improved to prevent duplicate events and consolidate existing ones.

## Problem
When uploading books from admin with "Sammelan Events", multiple separate event entries were being created instead of grouping books under the same event category.

## Solutions Implemented

### 1. **Unique Event Names**
- Event names are now unique in the database
- Prevents creating events with identical names
- Migration handles existing duplicates by adding IDs to duplicate names

### 2. **Improved Admin Interface**
- Events are ordered alphabetically for easier selection
- Warning messages when creating potentially duplicate events
- Help text guides users to reuse existing events
- JavaScript validation provides real-time feedback

### 3. **Event Consolidation Command**
Run this command to consolidate existing duplicate events:

```bash
# Dry run (preview changes without making them)
python manage.py consolidate_events --dry-run

# Consolidate all duplicate events
python manage.py consolidate_events

# Only consolidate Sammelan-related events
python manage.py consolidate_events --sammelan-only
```

### 4. **Smart Event Selection**
- The Event model includes logic to find existing similar events
- Suggests existing events when creating new ones
- Prevents near-duplicates (case-insensitive matching)

## Best Practices for Admin Users

### When Uploading Books:

1. **Check Existing Events First**
   - Before creating a new event, scroll through the event dropdown
   - Look for existing events that match your needs

2. **For Sammelan Books**
   - Use the existing "Sammelan Events" category
   - Don't create "Sammelan Events 2", "Sammelan Event", etc.

3. **Event Naming**
   - Use clear, consistent names
   - Avoid adding numbers unless they represent actual different events
   - Example: Use "Annual Conference" instead of "Annual Conference 1", "Annual Conference 2"

### Event Management:

1. **Creating New Events**
   - Only create a new event if it's genuinely different from existing ones
   - Check the admin will warn you about potential duplicates

2. **Consolidating Events**
   - Run the consolidate command periodically to clean up duplicates
   - Use --dry-run first to see what would be changed

## Technical Details

### Database Changes
- `Event.name` field is now unique
- Migration 0008 handles existing duplicates

### New Files Created
- `books/management/commands/consolidate_events.py` - Consolidation command
- `static/admin/js/event_admin.js` - Admin interface enhancements
- `templates/admin/books/event/change_list.html` - Help documentation

### Model Improvements
- Added validation to prevent duplicate events
- Added helper methods for finding similar events
- Better error messages for duplicate attempts

## Troubleshooting

### If you see "Event already exists" error:
1. Check the existing events list
2. Use the existing event instead of creating a new one
3. If you need to create a genuinely different event, use a more specific name

### To view what events will be consolidated:
```bash
python manage.py consolidate_events --dry-run
```

### To consolidate only Sammelan events:
```bash
python manage.py consolidate_events --sammelan-only
```

## Result
- No more duplicate events in the frontend
- All books with similar event names grouped under single events
- Better admin experience with warnings and guidance
- Easy management of event consolidation