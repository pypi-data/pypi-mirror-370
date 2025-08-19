//
//  IrisCodecCache.cpp
//  Iris
//
//  Created by Ryan Landvater on 4/14/24.
//

#include "IrisCodecPriv.hpp"

namespace IrisCodec {
inline bool VALIDATE_CACHE_TYPE (CacheEncoding encoding)
{
    switch (encoding) {
        case CACHE_ENCODING_IRIS:
        case CACHE_ENCODING_JPEG:
        case CACHE_ENCODING_AVIF:
        case CACHE_ENCODING_LZ:
        case CACHE_ENCODING_NO_COMPRESSION: return true;
        case CACHE_ENCODING_UNDEFINED: return false;
    } return false;
}
Cache create_cache (const CacheCreateInfo& info) noexcept
{
    try {
        if (VALIDATE_CACHE_TYPE(info.encodingType) == false)
            throw std::runtime_error("invalid cache encoding type in CacheCreateInfo");
        
        // Create a context if not provided
        Context context = info.context;
        if (context == nullptr) {
            ContextCreateInfo context_info {};
            context = std::make_shared<__INTERNAL__Context>(context_info);
        }
        if (context == nullptr)
            throw std::runtime_error("no valid context");
        
        auto file = create_cache_file(info);
        if (file == nullptr)
            throw std::runtime_error("no valid file opened.");
        
        // Create the slide object
        Cache   cache = std::make_shared<__INTERNAL__Cache>(info,file);
        if (cache == nullptr) throw std::runtime_error("Failed to create cache object");
        
        // Return the slide
        return cache;
        
    } catch (std::runtime_error &e) {
        std::cerr   << "Failed to create a slide cache: "
                    << e.what() << "\n";
        return nullptr;
    }
}
__INTERNAL__Cache::__INTERNAL__Cache (const CacheCreateInfo& info, const File& file) :
__INTERNAL__Slide   (info.context, file),
_codec              (info.encodingType)
{
    
}
} // END IRISCODEC

