#!/usr/bin/env python
"""
Test script to identify issues with the properties API endpoint.
This script will help diagnose 500 errors in production.
"""

import os
import sys
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realEstateWeb.settings')
django.setup()

from app.models import Property, PropertyType
from app.serializers import PropertySerializer
from django.core.exceptions import ValidationError
import traceback

def test_property_model():
    """Test Property model methods for potential issues"""
    print("=" * 50)
    print("TESTING PROPERTY MODEL METHODS")
    print("=" * 50)
    
    try:
        properties = Property.objects.all()
        print(f"Total properties in database: {properties.count()}")
        
        for prop in properties:
            print(f"\nTesting property: {prop.title}")
            print(f"  ID: {prop.id}")
            
            # Test each property method that could cause issues
            try:
                print(f"  formatted_area: {prop.formatted_area}")
            except Exception as e:
                print(f"  ERROR in formatted_area: {e}")
                traceback.print_exc()
            
            try:
                print(f"  purpose_display: {prop.purpose_display}")
            except Exception as e:
                print(f"  ERROR in purpose_display: {e}")
                traceback.print_exc()
            
            try:
                print(f"  area_in_sqft: {prop.area_in_sqft}")
            except Exception as e:
                print(f"  ERROR in area_in_sqft: {e}")
                traceback.print_exc()
            
            try:
                print(f"  formatted_land_area: {prop.formatted_land_area}")
            except Exception as e:
                print(f"  ERROR in formatted_land_area: {e}")
                traceback.print_exc()
            
            try:
                print(f"  land_area_display: {prop.land_area_display}")
            except Exception as e:
                print(f"  ERROR in land_area_display: {e}")
                traceback.print_exc()
            
            try:
                print(f"  google_maps_embed_src: {prop.google_maps_embed_src}")
            except Exception as e:
                print(f"  ERROR in google_maps_embed_src: {e}")
                traceback.print_exc()
                
    except Exception as e:
        print(f"ERROR accessing properties: {e}")
        traceback.print_exc()

def test_property_serialization():
    """Test Property serialization for potential issues"""
    print("\n" + "=" * 50)
    print("TESTING PROPERTY SERIALIZATION")
    print("=" * 50)
    
    try:
        properties = Property.objects.all()
        
        for prop in properties:
            print(f"\nTesting serialization for: {prop.title}")
            
            try:
                serializer = PropertySerializer(prop)
                data = serializer.data
                print(f"  Serialization successful")
                print(f"  Data keys: {list(data.keys())}")
                
                # Check for problematic fields
                problematic_fields = ['formatted_area', 'purpose_display', 'area_in_sqft', 
                                    'formatted_land_area', 'land_area_display', 'google_maps_embed_src']
                
                for field in problematic_fields:
                    if field in data:
                        print(f"  {field}: {data[field]}")
                    else:
                        print(f"  {field}: NOT FOUND")
                        
            except Exception as e:
                print(f"  ERROR in serialization: {e}")
                traceback.print_exc()
                
    except Exception as e:
        print(f"ERROR in serialization test: {e}")
        traceback.print_exc()

def test_property_queryset():
    """Test Property queryset operations"""
    print("\n" + "=" * 50)
    print("TESTING PROPERTY QUERYSET OPERATIONS")
    print("=" * 50)
    
    try:
        # Test the same queryset used in the view
        queryset = Property.objects.filter(is_active=True).select_related('property_type').prefetch_related('images')
        print(f"Active properties count: {queryset.count()}")
        
        for prop in queryset:
            print(f"  Property: {prop.title}")
            print(f"    Property Type: {prop.property_type}")
            print(f"    Images count: {prop.images.count()}")
            
    except Exception as e:
        print(f"ERROR in queryset test: {e}")
        traceback.print_exc()

def check_database_integrity():
    """Check for database integrity issues"""
    print("\n" + "=" * 50)
    print("CHECKING DATABASE INTEGRITY")
    print("=" * 50)
    
    try:
        # Check for properties with missing property_type
        properties_without_type = Property.objects.filter(property_type__isnull=True)
        print(f"Properties without property_type: {properties_without_type.count()}")
        
        # Check for properties with invalid data
        all_properties = Property.objects.all()
        for prop in all_properties:
            issues = []
            
            if prop.property_type is None:
                issues.append("Missing property_type")
            
            if prop.price is None:
                issues.append("Missing price")
            
            if prop.bathrooms is None:
                issues.append("Missing bathrooms")
            
            if issues:
                print(f"  Property '{prop.title}' has issues: {', '.join(issues)}")
                
    except Exception as e:
        print(f"ERROR in database integrity check: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    print("Starting Property API Diagnostic Test")
    print("This script will help identify issues causing 500 errors")
    
    test_property_model()
    test_property_serialization()
    test_property_queryset()
    check_database_integrity()
    
    print("\n" + "=" * 50)
    print("DIAGNOSTIC TEST COMPLETED")
    print("=" * 50)
    print("If no errors were shown above, the issue might be:")
    print("1. Production environment differences (DEBUG=False)")
    print("2. Missing dependencies in production")
    print("3. Database differences between dev and production")
    print("4. File permissions or static file issues")
    print("5. Server configuration issues")
