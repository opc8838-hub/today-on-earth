import { SITE } from "@/lib/constants";

interface UploadFormData {
  date: string;
  time_slot: "morning" | "afternoon";
  title: string;
  countries: string;
  cities: string;
}

interface VideoUploadFormProps {
  onSubmit: (data: UploadFormData, files: {
    horizontalVideo: File | null;
    horizontalCover: File | null;
  }) => Promise<void>;
  loading: boolean;
}

export function VideoUploadForm({ onSubmit, loading }: VideoUploadFormProps) {
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const form = e.currentTarget;
    const formData = new FormData(form);

    const data: UploadFormData = {
      date: formData.get("date") as string,
      time_slot: formData.get("time_slot") as "morning" | "afternoon",
      title: formData.get("title") as string,
      countries: formData.get("countries") as string,
      cities: formData.get("cities") as string,
    };

    const files = {
      horizontalVideo: formData.get("horizontal_video") as File | null,
      horizontalCover: formData.get("horizontal_cover") as File | null,
    };

    await onSubmit(data, files);
    form.reset();
  };

  const today = new Date().toISOString().split("T")[0];

  return (
    <form
      onSubmit={handleSubmit}
      className="bg-earth-800 border border-earth-700 rounded-lg p-6 space-y-4"
    >
      <h2 className="text-sm font-medium text-earth-100 tracking-wider">
        Upload Video &middot; 上传视频
      </h2>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {/* Date */}
        <div>
          <label className="block text-[10px] text-earth-500 mb-1 uppercase tracking-wider">
            Date
          </label>
          <input
            type="date"
            name="date"
            defaultValue={today}
            required
            className="w-full px-3 py-2 rounded-md bg-earth-900 border border-earth-600 text-earth-100 text-sm focus:outline-none focus:border-earth-blue"
          />
        </div>

        {/* Time Slot */}
        <div>
          <label className="block text-[10px] text-earth-500 mb-1 uppercase tracking-wider">
            Time Slot
          </label>
          <select
            name="time_slot"
            defaultValue="morning"
            required
            className="w-full px-3 py-2 rounded-md bg-earth-900 border border-earth-600 text-earth-100 text-sm focus:outline-none focus:border-earth-blue"
          >
            <option value="morning">Morning Earth</option>
            <option value="afternoon">Afternoon Earth</option>
          </select>
        </div>

        {/* Title */}
        <div className="sm:col-span-2">
          <label className="block text-[10px] text-earth-500 mb-1 uppercase tracking-wider">
            Title (optional)
          </label>
          <input
            type="text"
            name="title"
            placeholder={`${SITE.name} — Morning Earth`}
            className="w-full px-3 py-2 rounded-md bg-earth-900 border border-earth-600 text-earth-100 text-sm focus:outline-none focus:border-earth-blue placeholder:text-earth-600"
          />
        </div>

        {/* Countries */}
        <div>
          <label className="block text-[10px] text-earth-500 mb-1 uppercase tracking-wider">
            Countries (comma separated)
          </label>
          <input
            type="text"
            name="countries"
            placeholder="Japan, Thailand, Brazil"
            className="w-full px-3 py-2 rounded-md bg-earth-900 border border-earth-600 text-earth-100 text-sm focus:outline-none focus:border-earth-blue placeholder:text-earth-600"
          />
        </div>

        {/* Cities */}
        <div>
          <label className="block text-[10px] text-earth-500 mb-1 uppercase tracking-wider">
            Cities (comma separated)
          </label>
          <input
            type="text"
            name="cities"
            placeholder="Tokyo, Bangkok, Rio de Janeiro"
            className="w-full px-3 py-2 rounded-md bg-earth-900 border border-earth-600 text-earth-100 text-sm focus:outline-none focus:border-earth-blue placeholder:text-earth-600"
          />
        </div>

        {/* Files */}
        <div>
          <label className="block text-[10px] text-earth-500 mb-1 uppercase tracking-wider">
            Horizontal Video (.mp4)
          </label>
          <input
            type="file"
            name="horizontal_video"
            accept="video/mp4"
            required
            className="w-full text-xs text-earth-300 file:mr-3 file:py-1.5 file:px-3 file:rounded-md file:border-0 file:text-xs file:bg-earth-700 file:text-earth-300 hover:file:bg-earth-600"
          />
        </div>

        <div>
          <label className="block text-[10px] text-earth-500 mb-1 uppercase tracking-wider">
            Cover Image (.jpg/.png)
          </label>
          <input
            type="file"
            name="horizontal_cover"
            accept="image/jpeg,image/png"
            className="w-full text-xs text-earth-300 file:mr-3 file:py-1.5 file:px-3 file:rounded-md file:border-0 file:text-xs file:bg-earth-700 file:text-earth-300 hover:file:bg-earth-600"
          />
        </div>
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full py-2.5 rounded-md bg-earth-blue text-white text-sm font-medium hover:bg-earth-blue/80 transition-colors disabled:opacity-40"
      >
        {loading ? "Uploading…" : "Upload & Publish"}
      </button>
    </form>
  );
}
