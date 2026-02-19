from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.routers.project import router as project_router
from app.api.routers.places import router as place_router
from app.services.artic_place_fetcher.artic_place_fetcher import ArticPlaceFetcher
import asyncio
from datetime import datetime
from app.services.travel_manager.errors.errors import *
from app.services.artic_place_fetcher.errors.errors import *
from app.services.travel_manager.travel_manager import TravelManager
from app.api.models.models import *

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup Logic ---
    # Initialize the Singleton Fetcher and load data into memory
    fetcher = ArticPlaceFetcher()
    print("Initializing Artic Place Fetcher cache...")
    await fetcher.fetch_all_places()
    print(f"Successfully cached {len(fetcher._places)} locations.")
    
    yield
    # --- Shutdown Logic ---
    print("Shutting down Travel Planner API...")

# Initialize FastAPI with the lifespan handler
app = FastAPI(
    title="Travel Planner API",
    version="1.0.0",
    lifespan=lifespan
)

# Include your routers
app.include_router(project_router)
app.include_router(place_router)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    async def debug_session():
        print("\n🚀 --- STARTING DEBUG SESSION --- 🚀")
        
        # 1. Initialize Fetcher (Simulating Lifespan Startup)
        fetcher = ArticPlaceFetcher()
        print("📥 Fetching Artic Data (this may take a few seconds)...")
        await fetcher.fetch_all_places()
        print(f"✅ Cache Loaded: {len(fetcher._places)} places available.")

        # 2. Initialize Manager
        manager = TravelManager()

        try:
            # 3. Test Project Creation
            print("\n📝 Creating 'Chicago Weekend' Project...")
            new_project_data = ProjectCreate(
                name="Chicago Weekend",
                description="Exploring the Windy City",
                start_date=datetime(2026, 5, 20),
                places=[]
            )
            # Use await because create_project calls the async fetcher
            project, warnings = await manager.create_project(new_project_data)
            print(f"✅ Project Created with ID: {project._id}")

            # 4. Test Adding Places (Validation & Business Rules)
            print("\n📍 Adding Places...")
            # We'll use a name we know exists (assuming "Modern Wing" is in Artic)
            # You can check your logs to pick a real name from the fetcher
            place_to_add = PlaceCreate(name="Izumo", note="Check the architecture")
            
            # Using the method we just implemented
            new_place = await manager.add_place_to_project(project._id, place_to_add)
            print(f"✅ Added Place: {new_place.name} (ID: {new_place.id})")

            # 5. Test Deletion Guard (Should allow now)
            print(f"\n🗑️ Testing Deletion (Visited: False)...")
            print(f"Is deletable? {project.is_deletable()}")

            # 6. Test 'Mark Visited' and Deletion Guard
            print("\n🚩 Marking Place as Visited...")
            manager.mark_place_visited(project._id, new_place.id)
            print(f"Is deletable now? {project.is_deletable()}")

            # 7. Test Expected Failure: Deleting a project with visited places
            print("\n❌ Testing Illegal Deletion...")
            try:
                manager.remove_project(project._id)
            except ProjectIsNotDeletableError:
                print("✅ Successfully blocked deletion of project with visited places.")

            # 8. Test Name Filter Logic
            print("\n🔍 Testing List Filtering...")
            results = manager.list_projects()
            filtered = [p for p in results if "Chicagoss" in p.name]
            print(f"Found {len(filtered)} projects matching 'Chicagoss'")

        except Exception as e:
            print(f"⚠️ DEBUG FAILED: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()

        print("\n🏁 --- DEBUG SESSION COMPLETE --- 🏁")

        # --- STRESS TESTING ---
        print("\n🔥 --- STARTING STRESS TESTS --- 🔥")

        # 1. Test Duplicate Place Prevention
        print("Testing Duplicate Place Entry...")
        try:
            # We already added "Modern Wing" (ID 123)
            # Let's try to add it again
            duplicate_place = PlaceCreate(name="Izumo", note="Trying to double add")
            await manager.add_place_to_project(project._id, duplicate_place)
            print("❌ FAILURE: Manager allowed a duplicate place!")
        except DuplicatePlaceError:
            print("✅ SUCCESS: Correcty blocked duplicate place.")

        # 2. Test Project Capacity (Max 10 Places)
        print("\nTesting Project Capacity (Limit: 10)...")
        # We currently have 1 place. Let's try to add 11 more.
        # Note: You'll need real names that exist in your Fetcher cache for this to work
        test_names = [ArticPlaceFetcher().get_random_place_name() for _ in range(1, 12)] 
        
        try:
            for name in test_names:
                p_data = PlaceCreate(name=name, note="Capacity Test")
                await manager.add_place_to_project(project._id, p_data)
                print(f"   Added {name}...")
            
            print("❌ FAILURE: Manager allowed more than 10 places!")
        except ProjectHasMaxPlacesAllowedError:
            print(f"✅ SUCCESS: Blocked addition at place limit (Current count: {len(project._project_places)})")

    # Run the async loop
    asyncio.run(debug_session())